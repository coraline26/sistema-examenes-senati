import sqlite3

ID_PREGUNTA = 5  # cambia el ID

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE preguntas
SET pregunta = ?,
    opcion_a = ?,
    opcion_b = ?,
    opcion_c = ?,
    opcion_d = ?,
    respuesta_correcta = ?
WHERE id = ?
""", (
    "¿Qué es liderazgo efectivo?",
    "Mandar",
    "Influir positivamente",
    "Controlar",
    "Gritar",
    "B",
    ID_PREGUNTA
))

conn.commit()
conn.close()

print("✅ Pregunta actualizada")
