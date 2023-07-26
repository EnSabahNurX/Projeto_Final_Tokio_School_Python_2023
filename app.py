import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pytz
from models.models import Vehicle  # Importe a classe Vehicle do arquivo models.py


app = Flask(__name__)

# Configurar o fuso horário de Portugal
app.config['TIMEZONE'] = pytz.timezone('Europe/Lisbon')

# Caminho do banco de dados
db_folder = os.path.join(os.path.dirname(__file__), 'database')
db_path = os.path.join(db_folder, 'database.db')

# Configurações do SQLite - banco de dados ficará dentro da pasta 'database'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar a extensão SQLAlchemy
db = SQLAlchemy(app)

# Rota inicial
@app.route('/')
def index():
    # Consultar todos os veículos no banco de dados
    vehicles = Vehicle.query.all()
    return render_template('index.html', vehicles=vehicles)

# Rota para a página de login do administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Administradores temporários (em um projeto real, deve ser armazenado de forma segura)
    admins = {'admin': 'password'}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admins and admins[username] == password:
            return redirect(url_for('admin_panel'))

    return render_template('login.html')

# Rota para o painel de administração
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    # Aqui você pode implementar a lógica para adicionar, editar e excluir veículos no banco de dados.
    # Por enquanto, vamos apenas exibir uma mensagem de boas-vindas.
    return "Bem-vindo ao Painel de Administração!"

# Verificar e criar o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == '__main__':
    app.run(debug=True)
