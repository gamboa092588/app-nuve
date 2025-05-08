import os
import sqlite3
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'

UPLOAD_FOLDER = 'uploads'
EXTENSOES_PERMITIDAS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

def obter_conexao():
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.errorhandler(413)
def limite_arquivo_excedido(e):
    return "Arquivo muito grande. Limite de 20MB.", 413

@app.route('/')
def index():
    if 'usuario' in session:
        pasta_usuario = os.path.join(UPLOAD_FOLDER, session['usuario'])
        if not os.path.exists(pasta_usuario):
            os.makedirs(pasta_usuario)
        arquivos = os.listdir(pasta_usuario)
        return render_template('index.html', usuario=session['usuario'], arquivos=arquivos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT senha_hash FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conn.close()
        if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario['senha_hash']):
            session['usuario'] = email
            return redirect(url_for('index'))
        else:
            return 'Login inválido'
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        conn = obter_conexao()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (email, senha_hash) VALUES (?, ?)", (email, senha_hash))
            conn.commit()
            session['usuario'] = email
            pasta_usuario = os.path.join(UPLOAD_FOLDER, email)
            if not os.path.exists(pasta_usuario):
                os.makedirs(pasta_usuario)
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return 'Usuário já cadastrado'
        finally:
            conn.close()
    return render_template('cadastro.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    arquivo = request.files['arquivo']
    if arquivo and arquivo_permitido(arquivo.filename):
        nome_seguro = secure_filename(arquivo.filename)
        pasta_usuario = os.path.join(UPLOAD_FOLDER, session['usuario'])
        if not os.path.exists(pasta_usuario):
            os.makedirs(pasta_usuario)
        caminho = os.path.join(pasta_usuario, nome_seguro)
        arquivo.save(caminho)
        return redirect(url_for('index'))
    else:
        return 'Tipo de arquivo não permitido.', 400

@app.route('/download/<nome_arquivo>')
def download(nome_arquivo):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    pasta_usuario = os.path.join(UPLOAD_FOLDER, session['usuario'])
    return send_from_directory(pasta_usuario, nome_arquivo)

if __name__ == '__main__':
    app.run(debug=False)


