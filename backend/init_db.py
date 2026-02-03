import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "examenes.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

"""cursor.execute(
CREATE TABLE IF NOT EXISTS preguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_examen TEXT,
    pregunta TEXT,
    opcion_a TEXT,
    opcion_b TEXT,
    opcion_c TEXT,
    opcion_d TEXT,
    respuesta_correcta TEXT
)
)

conn.commit()
conn.close()
"""

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL
)
""")

# Crear usuario admin por defecto
cursor.execute("""
INSERT OR IGNORE INTO usuarios (username, password, rol)
VALUES ('admin', 'admin123', 'admin')
""")

conn.commit()
conn.close()

print("✅ Base de datos inicializada correctamente")