import sqlite3

# Conecta ao banco (vai criar se não existir)
conn = sqlite3.connect('usuarios.db')
cursor = conn.cursor()

# Cria a tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL
)
''')

conn.commit()
conn.close()
print("Banco de dados criado com sucesso!")
