import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "examenes.db")

from database import get_connection

def login(dni, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT carrera, nombres
        FROM usuarios
        WHERE dni = ? AND password = ?
    """, (dni, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        return {
            "dni": dni,
            "carrera": user["carrera"],
            "nombres": user["nombres"]
        }
    return None


def crear_usuario(username, password, rol):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO usuarios (username, password, rol)
            VALUES (?, ?, ?)
        """, (username, password, rol))

        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
