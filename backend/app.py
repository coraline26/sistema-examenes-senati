from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from flask import render_template
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import pandas as pd
import os

# Esto le dice a Flask que busque las carpetas dentro de la carpeta actual
current_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            template_folder=os.path.join(current_dir, 'templates'),
            static_folder=os.path.join(current_dir, 'static'))

from models import (
    obtener_preguntas_aleatorias,
    crear_pregunta,
    editar_pregunta,
    eliminar_pregunta,
    eliminar_usuario,
    listar_usuarios,
    verificar_respuestas,
    guardar_resultado
)
from database import get_connection

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "super-clave-secreta-123"
jwt = JWTManager(app)

# ------------------------
# HOME
# ------------------------
@app.route("/")
def home():
    #return jsonify({"status": "API funcionando correctamente"})
    return render_template('index.html') # Esto cargará tu archivo de la carpeta templates
# ------------------------
# LOGIN
# ------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    dni = data.get("dni")
    password = data.get("password")

    if not dni or not password:
        return jsonify({"mensaje": "Datos incompletos"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dni, nombres, carrera
        FROM usuarios
        WHERE dni = ? AND password = ?
    """, (dni, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"mensaje": "Credenciales incorrectas"}), 401

    token = create_access_token(identity=user["dni"])

    return jsonify({
        "token": token,
        "dni": user["dni"],
        "nombres": user["nombres"],
        "carrera": user["carrera"]
    })

# ------------------------
# PERFIL (PRUEBA JWT)
# ------------------------
@app.route("/perfil")
@jwt_required()
def perfil():
    return jsonify({
        "mensaje": "Acceso autorizado",
        "dni": get_jwt_identity()
    })

# ------------------------
# EXAMEN AUTOMÁTICO
# ------------------------
@app.route("/examen_auto", methods=["GET"])
@jwt_required()
def examen_auto():
    dni = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT carrera FROM usuarios WHERE dni = ?", (dni,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    carrera = user["carrera"]
    preguntas = obtener_preguntas_aleatorias(carrera)

    if not preguntas:
        return jsonify({"mensaje": "No hay preguntas para esta carrera"}), 404

    return jsonify({
        "carrera": carrera,
        "total": len(preguntas),
        "preguntas": preguntas
    })

# ------------------------
# ENVÍO DE EXAMEN (ACTIVO Y CORRECTO)
# ------------------------
@app.route("/enviar_examen", methods=["POST"])
@jwt_required()
def enviar_examen():
    data = request.json
    dni = get_jwt_identity()

    respuestas = data.get("respuestas")
    if not respuestas:
        return jsonify({"mensaje": "No se recibieron respuestas"}), 400

    puntaje = verificar_respuestas(respuestas)
    total = len(respuestas)
    nota = round((puntaje / total) * 20, 2)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombres, carrera FROM usuarios WHERE dni = ?
    """, (dni,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    guardar_resultado(
        dni,
        user["nombres"],
        user["carrera"],
        puntaje,
        total,
        nota
    )

    return jsonify({
        "puntaje": puntaje,
        "total": total,
        "nota": nota
    })


# ------------------------
# ADMIN - PREGUNTAS
# ------------------------
@app.route("/admin/pregunta", methods=["POST"])
def admin_crear_pregunta():
    crear_pregunta(request.json)
    return jsonify({"mensaje": "Pregunta creada correctamente"})

@app.route("/admin/pregunta/<int:id_pregunta>", methods=["PUT"])
def admin_editar_pregunta(id_pregunta):
    editar_pregunta(id_pregunta, request.json)
    return jsonify({"mensaje": "Pregunta actualizada"})

@app.route("/admin/pregunta/<int:id_pregunta>", methods=["DELETE"])
def admin_eliminar_pregunta(id_pregunta):
    eliminar_pregunta(id_pregunta)
    return jsonify({"mensaje": "Pregunta eliminada"})

# ------------------------
# ADMIN - USUARIOS
# ------------------------
@app.route("/admin/usuarios")
def admin_listar_usuarios():
    return jsonify(listar_usuarios())

@app.route("/admin/usuario/<int:id_usuario>", methods=["DELETE"])
def admin_eliminar_usuario(id_usuario):
    eliminar_usuario(id_usuario)
    return jsonify({"mensaje": "Usuario eliminado"})

# ------------------------
# ADMIN - RESULTADOS
# ------------------------
@app.route("/admin/resultados")
@jwt_required()
def admin_resultados():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT dni, nombres, carrera, puntaje, total, nota, fecha
        FROM resultados
        ORDER BY fecha DESC
    """)

    resultados = [dict(f) for f in cursor.fetchall()]
    conn.close()

    return jsonify(resultados)

# ------------------------
# ADMIN - EXPORTAR EXCEL
# ------------------------
@app.route("/admin/exportar_excel", methods=["GET"])
@jwt_required()
def exportar_excel():
    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT dni, nombres, carrera, puntaje, total, nota, fecha
        FROM resultados
        ORDER BY fecha DESC
    """, conn)

    conn.close()

    carpeta = "reportes"
    os.makedirs(carpeta, exist_ok=True)

    archivo = os.path.join(carpeta, "reporte_examenes.xlsx")
    df.to_excel(archivo, index=False)

    return send_file(
        archivo,
        as_attachment=True,
        download_name="reporte_examenes.xlsx",
        mimetype="application/vnd.openxmlformats-officedsheetml.sheet"
    )

# ------------------------
# ADMIN - DASHBOARD
# ------------------------
@app.route("/admin/dashboard")
@jwt_required()
def admin_dashboard():
    dni = get_jwt_identity()

    conn = get_connection()
    cursor = conn.cursor()

    # Verificar que sea ADMIN
    cursor.execute("""
        SELECT carrera FROM usuarios WHERE dni = ?
    """, (dni,))
    user = cursor.fetchone()

    if not user or user["carrera"] != "ADMIN":
        conn.close()
        return jsonify({"mensaje": "Acceso denegado"}), 403

    # Total de exámenes
    cursor.execute("SELECT COUNT(*) as total FROM resultados")
    total = cursor.fetchone()["total"]

    # Promedio general
    cursor.execute("SELECT AVG(nota) as promedio FROM resultados")
    promedio = cursor.fetchone()["promedio"]
    promedio = round(promedio, 2) if promedio else 0

    # Historial
    cursor.execute("""
        SELECT dni, nombres, carrera, puntaje, nota, fecha
        FROM resultados
        ORDER BY fecha DESC
    """)
    historial = [dict(f) for f in cursor.fetchall()]

    conn.close()

    return jsonify({
        "total": total,
        "promedio": promedio,
        "historial": historial
    })

@app.route("/admin/alumno", methods=["POST"])
@jwt_required()
def crear_alumno():
    data = request.json

    dni = data.get("dni")
    password = data.get("password")
    nombres = data.get("nombres")
    carrera = data.get("carrera")

    if not dni or not password or not nombres or not carrera:
        return jsonify({"mensaje": "Datos incompletos"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # 🔒 Verificar duplicado
    cursor.execute("SELECT 1 FROM usuarios WHERE dni = ?", (dni,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"mensaje": "El DNI ya existe"}), 400

    cursor.execute("""
        INSERT INTO usuarios (dni, password, nombres, carrera)
        VALUES (?, ?, ?, ?)
    """, (dni, password, nombres, carrera))

    conn.commit()
    conn.close()

    return jsonify({"mensaje": "Alumno registrado correctamente"})


# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    print(">>> app.py se está ejecutando")
    app.run(debug=True)
