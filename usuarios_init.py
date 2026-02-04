import sqlite3

conn = sqlite3.connect("examenes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    rol TEXT
)
""")

# usuario administrador por defecto
cursor.execute("""
INSERT OR IGNORE INTO usuarios (username, password, rol)
VALUES ('admin', 'admin123', 'admin')
""")

conn.commit()
conn.close()

print("Usuarios inicializados correctamente")
