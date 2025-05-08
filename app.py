from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta_simples'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Criar pasta de uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Usuários simulados (futuro: banco de dados)
usuarios = {
    'teste@email.com': '1234'
}

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
        if email in usuarios and usuarios[email] == senha:
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
            usuarios[email] = senha
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
    if arquivo:
        nome_seguro = secure_filename(arquivo.filename)
        caminho = os.path.join(UPLOAD_FOLDER, session['usuario'], nome_seguro)
        arquivo.save(caminho)
    return redirect(url_for('index'))

@app.route('/download/<nome_arquivo>')
def download(nome_arquivo):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return send_from_directory(os.path.join(UPLOAD_FOLDER, session['usuario']), nome_arquivo)

if __name__ == '__main__':
    # Evitar debug=True em ambientes com restrições de multiprocessing
    app.run(debug=False)
