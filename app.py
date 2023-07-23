import os
import pytz
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import timedelta


app = Flask(__name__)
app.secret_key = 'chave_secreta_aqui'

# Configuração para usar o fuso horário de Portugal
app.config['TIMEZONE'] = 'Europe/Lisbon'

# Verifica se o diretório "database" existe e, se não existir, cria-o
database_dir = os.path.join(app.root_path, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Configuração do URI do banco de dados SQLite
db_path = os.path.join(database_dir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Definição das classes Carro, Mota e Disponibilidade


class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(200), default='default_car.png')
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    diaria = db.Column(db.Float, nullable=False)
    combustivel = db.Column(db.String(50), nullable=False)
    lugares = db.Column(db.Integer, nullable=False)
    potencia = db.Column(db.String(50), nullable=False)
    transmissao = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    utilizacoes = db.Column(db.Integer, default=0)
    limite_utilizacoes = db.Column(db.Integer, nullable=False, default=5)
    data_legalizacao = db.Column(db.Date, nullable=False)
    data_alerta_legalizacao = db.Column(db.Date, nullable=False)


class Mota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(200), default='default_mota.png')
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    diaria = db.Column(db.Float, nullable=False)
    cilindradas = db.Column(db.String(50), nullable=False)
    peso = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    utilizacoes = db.Column(db.Integer, default=0)
    limite_utilizacoes = db.Column(db.Integer, nullable=False, default=3)
    data_legalizacao = db.Column(db.Date, nullable=False)
    data_alerta_legalizacao = db.Column(db.Date, nullable=False)


class Disponibilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'), nullable=True)
    carro = db.relationship('Carro', backref=db.backref(
        'disponibilidades', lazy=True))
    mota_id = db.Column(db.Integer, db.ForeignKey('mota.id'), nullable=True)
    mota = db.relationship('Mota', backref=db.backref(
        'disponibilidades', lazy=True))
    data_disponivel = db.Column(db.Date, nullable=False)

# Definição da classe User para armazenar as credenciais do administrador


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Event Listener para calcular a data de alerta antes de salvar o registro


@db.event.listens_for(Carro, 'before_insert')
@db.event.listens_for(Carro, 'before_update')
@db.event.listens_for(Mota, 'before_insert')
@db.event.listens_for(Mota, 'before_update')
def calculate_alert_date(mapper, connection, target):
    if target.data_legalizacao:
        # Obtém o fuso horário de Portugal
        tz = pytz.timezone(app.config['TIMEZONE'])

        # Converte a data de legalização para o fuso horário de Portugal
        data_legalizacao_portugal = tz.localize(target.data_legalizacao)

        # Calcula a data de alerta para legalização (30 dias antes)
        data_alerta_legalizacao = data_legalizacao_portugal - \
            timedelta(days=30)

        # Converte a data de alerta de volta para o formato local de Portugal
        target.data_alerta_legalizacao = data_alerta_legalizacao.date()


# Criação das tabelas do banco de dados
if not os.path.exists('database.db'):
    with app.app_context():
        db.create_all()
        # db.session.commit()
else:
    with app.app_context():
        db.session.commit()


# Definição das rotas
# Rota da página inicial
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/carros')
def listar_carros():
    return 'Listagem de carros'


@app.route('/carros/<int:carro_id>')
def exibir_carro(carro_id):
    return f'Detalhes do carro {carro_id}'



# Rota para a página de login do administrador
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verifica as credenciais do administrador
        if username == 'admin' and password == 'admin':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'error')

    return render_template('admin_login.html')

# Rota para a página de administração após o login
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    # Verifica se o administrador está autenticado
    if not session.get('admin_logged_in'):
        flash('Acesso não autorizado. Faça login como administrador para continuar.', 'error')
        return redirect(url_for('admin_login'))

    # Obtenha os dados dos carros e motas do banco de dados (exemplo)
    carros = Carro.query.all()
    motas = Mota.query.all()

    if request.method == 'POST':
        tipo = request.form['tipo']
        marca = request.form['marca']
        modelo = request.form['modelo']
        diaria = float(request.form['diaria'])
        # Receba os demais campos do formulário e salve em suas respectivas variáveis

        # Verifica o tipo de veículo e insere no banco de dados (exemplo)
        if tipo.lower() == 'carro':
            novo_carro = Carro(marca=marca, modelo=modelo, diaria=diaria)
            # Preencha os demais campos do carro antes de adicionar ao banco de dados
            db.session.add(novo_carro)
            db.session.commit()
            flash('Carro adicionado com sucesso.', 'success')
        elif tipo.lower() == 'mota':
            nova_mota = Mota(marca=marca, modelo=modelo, diaria=diaria)
            # Preencha os demais campos da mota antes de adicionar ao banco de dados
            db.session.add(nova_mota)
            db.session.commit()
            flash('Mota adicionada com sucesso.', 'success')
        else:
            flash('Tipo de veículo inválido. Insira "Carro" ou "Mota".', 'error')

    return render_template('admin_dashboard.html', carros=carros, motas=motas)


# Rota para fazer o logout do administrador
@app.route('/admin/logout')
def admin_logout():
    # Limpa a sessão do administrador
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('admin_login'))





# Execução da app
if __name__ == '__main__':
    # O debug=True faz com que cada vez que reiniciemos o servidor ou modifiquemos o código, o servidor de Flask reinicia-se sozinho
    app.run(debug=True)
