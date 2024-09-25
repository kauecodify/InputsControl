import sqlite3

def create_database():

    conn = sqlite3.connect("gastos.db")

    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            ano INTEGER NOT NULL,
            semestre INTEGER NOT NULL,
            valor REAL NOT NULL,
            FOREIGN KEY (usuario) REFERENCES usuarios(usuario)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Banco de dados e tabelas criados com sucesso.")
