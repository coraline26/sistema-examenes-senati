import sqlite3

ID_PREGUNTA = 5  # ← cambia el número

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM preguntas WHERE id = ?", (ID_PREGUNTA,))

conn.commit()
conn.close()

print("✅ Pregunta eliminada")
