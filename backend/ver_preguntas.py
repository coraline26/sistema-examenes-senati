import sqlite3

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

cursor.execute("""
SELECT id, tipo_examen, pregunta
FROM preguntas
""")

for fila in cursor.fetchall():
    print(fila)

conn.close()
