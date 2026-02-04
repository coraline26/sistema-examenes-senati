import sqlite3
import csv

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

with open("preguntas_3.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=',')

    print("Encabezados detectados:", reader.fieldnames)

    for row in reader:
        cursor.execute("""
            INSERT INTO preguntas (
                tipo_examen, pregunta, opcion_a, opcion_b,
                opcion_c, opcion_d, respuesta_correcta
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row['tipo_examen'],
            row['pregunta'],
            row['opcion_a'],
            row['opcion_b'],
            row['opcion_c'],
            row['opcion_d'],
            row['respuesta_correcta']
        ))

conn.commit()
conn.close()

print("✅ Preguntas importadas correctamente")
