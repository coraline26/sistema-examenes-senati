import csv
import sqlite3
import os

ARCHIVO = "preguntas_3.csv"

if not os.path.exists(ARCHIVO):
    print(" ERROR: No se encontró preguntas.csv en la carpeta backend")
    exit()

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

contador = 0
invalidas = 0

with open(ARCHIVO, encoding="latin-1") as archivo:
    contenido = archivo.read().splitlines()

    # Detectar delimitador automáticamente
    delimitador = ";" if ";" in contenido[0] else ","

    lector = csv.reader(contenido, delimiter=delimitador)
    encabezado = next(lector, None)

    for fila in lector:
        if len(fila) != 7:
            print(" Fila inválida:", fila)
            invalidas += 1
            continue

        # Limpiar espacios
        fila = [c.strip() for c in fila]

        cursor.execute("""
            INSERT INTO preguntas
            (tipo_examen, pregunta, opcion_a, opcion_b, opcion_c, opcion_d, respuesta_correcta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, fila)

        contador += 1

conn.commit()
conn.close()

print(f" Carga completada. Preguntas insertadas: {contador}")
print(f" Filas inválidas: {invalidas}")
