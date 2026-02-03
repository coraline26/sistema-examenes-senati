from database import get_connection
import sqlite3


# ==============================
# EXÁMENES
# ==============================

def obtener_preguntas_aleatorias(tipo_examen):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, pregunta, opcion_a, opcion_b, opcion_c, opcion_d
        FROM preguntas
        WHERE tipo_examen = ?
        ORDER BY RANDOM()
        LIMIT 20
    """, (tipo_examen,))

    filas = cursor.fetchall()

    preguntas = []
    for f in filas:
        preguntas.append({
            "id": f["id"],
            "pregunta": f["pregunta"],
            "opcion_a": f["opcion_a"],
            "opcion_b": f["opcion_b"],
            "opcion_c": f["opcion_c"],
            "opcion_d": f["opcion_d"]
        })

    conn.close()
    return preguntas

def verificar_respuestas(respuestas):
    puntaje = 0
    conn = get_connection()
    cursor = conn.cursor()

    for r in respuestas:
        pregunta_id = int(r["id_pregunta"])   # 🔥 CLAVE
        respuesta_usuario = r["respuesta"]

        cursor.execute("""
            SELECT respuesta_correcta
            FROM preguntas
            WHERE id = ?
        """, (pregunta_id,))

        fila = cursor.fetchone()

        if fila and fila["respuesta_correcta"] == respuesta_usuario:
            puntaje += 1

    conn.close()
    return puntaje


# ==============================
# ADMIN - PREGUNTAS
# ==============================

def crear_pregunta(data):
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO preguntas
        (tipo_examen, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["tipo_examen"],
        data["pregunta"],
        data["opcion_a"],
        data["opcion_b"],
        data["opcion_c"],
        data["opcion_d"],
        data["respuesta_correcta"]
    ))

    conn.commit()
    conn.close()


def editar_pregunta(id_pregunta, data):
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE preguntas SET
            tipo_examen = ?,
            pregunta = ?,
            opcion_a = ?,
            opcion_b = ?,
            opcion_c = ?,
            opcion_d = ?,
            respuesta_correcta = ?
        WHERE id = ?
    """, (
        data["tipo_examen"],
        data["pregunta"],
        data["opcion_a"],
        data["opcion_b"],
        data["opcion_c"],
        data["opcion_d"],
        data["respuesta_correcta"],
        id_pregunta
    ))

    conn.commit()
    conn.close()


def eliminar_pregunta(id_pregunta):
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM preguntas WHERE id = ?", (id_pregunta,))
    conn.commit()
    conn.close()


# ==============================
# ADMIN - USUARIOS
# ==============================

def crear_usuario(data):
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usuarios (username, password, rol)
        VALUES (?, ?, ?)
    """, (
        data["username"],
        data["password"],
        data["rol"]
    ))

    conn.commit()
    conn.close()


def eliminar_usuario(id_usuario):
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
    conn.commit()
    conn.close()


def listar_usuarios():
    conn = sqlite3.connect("examenes.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, rol FROM usuarios")
    usuarios = cursor.fetchall()

    conn.close()
    return usuarios

def guardar_resultado(dni, carrera, puntaje, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resultados (dni, carrera, puntaje, total)
        VALUES (?, ?, ?, ?)
    """, (dni, carrera, puntaje, total))

    conn.commit()
    conn.close()

"""
def guardar_resultado(dni, puntaje, total):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        SELECT nombres, carrera FROM usuarios WHERE dni = ?
    , (dni,))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return

    nombres = user["nombres"]
    carrera = user["carrera"]
    nota = round((puntaje / total) * 20, 2)

    cursor.execute(
        INSERT INTO resultados (dni, nombres, carrera, puntaje, total, nota)
        VALUES (?, ?, ?, ?, ?, ?)
    , (dni, nombres, carrera, puntaje, total, nota))

    conn.commit()
    conn.close()
"""
def guardar_resultado(dni, nombres, carrera, puntaje, total, nota):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resultados 
        (dni, nombres, carrera, puntaje, total, nota)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (dni, nombres, carrera, puntaje, total, nota))

    conn.commit()
    conn.close()


