import os
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename

# Configuração inicial
app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB

EXTENSOES_PERMITIDAS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}

# Função auxiliar para validar extensão de arquivo
def arquivo_permitido(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Simulação de banco de dados
usuarios = {}

# Tratamento para arquivos muito grandes
@app.errorhandler(413)
def limite_arquivo_excedido(e):
    return "Arquivo muito grande. Limite de 20MB.", 413

@app.route('/')
def index():
    if 'usuario' in session:
        arquivos = os.listdir(os.path.join(UPLOAD_FOLDER, session['usuario']))
        return render_template('index.html', usuario=session['usuario'], arquivos=arquivos)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if email in usuarios and bcrypt.checkpw(senha.encode('utf-8'), usuarios[email]):
            session['usuario'] = email
            pasta_usuario = os.path.join(UPLOAD_FOLDER, email)
            if not os.path.exists(pasta_usuario):
                os.makedirs(pasta_usuario)
            return redirect(url_for('index'))
        else:
            return 'Login inválido'
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        if email not in usuarios:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            usuarios[email] = senha_hash
            session['usuario'] = email
            pasta_usuario = os.path.join(UPLOAD_FOLDER, email)
            if not os.path.exists(pasta_usuario):
                os.makedirs(pasta_usuario)
            return redirect(url_for('index'))
        else:
            return 'Usuário já cadastrado'
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
        caminho = os.path.join(UPLOAD_FOLDER, session['usuario'], nome_seguro)
        arquivo.save(caminho)
        return redirect(url_for('index'))
    else:
        return 'Tipo de arquivo não permitido.', 400

@app.route('/download/<nome_arquivo>')
def download(nome_arquivo):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return send_from_directory(os.path.join(UPLOAD_FOLDER, session['usuario']), nome_arquivo)

if __name__ == '__main__':
    app.run(debug=False)






