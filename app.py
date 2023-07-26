import os
import pytz
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from datetime import datetime,timedelta


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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

# Definição das classes Carro, Mota e Disponibilidade


class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    cor = db.Column(db.String(20), nullable=False)
    quilometragem = db.Column(db.Float, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    utilizacoes = db.Column(db.Integer, nullable=False)
    limite_utilizacoes = db.Column(db.Integer, nullable=False)
    potencia = db.Column(db.Integer)
    transmissao = db.Column(db.String(20))
    diaria = db.Column(db.Float, nullable=False)
    data_legalizacao = db.Column(db.Date, nullable=False)
    data_alerta_legalizacao = db.Column(db.Date)
    imagens = db.Column(db.String(255))  # Caminho das imagens

    def __repr__(self):
        return f'<Carro {self.marca} {self.modelo}>'


class Mota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    cor = db.Column(db.String(20), nullable=False)
    quilometragem = db.Column(db.Float, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    utilizacoes = db.Column(db.Integer, nullable=False)
    limite_utilizacoes = db.Column(db.Integer, nullable=False)
    cilindradas = db.Column(db.Integer)
    peso = db.Column(db.Float)
    diaria = db.Column(db.Float, nullable=False)
    data_legalizacao = db.Column(db.Date, nullable=False)
    data_alerta_legalizacao = db.Column(db.Date)
    imagens = db.Column(db.String(255))  # Caminho das imagens

    def __repr__(self):
        return f'<Mota {self.marca} {self.modelo}>'


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


@app.route('/motas')
def listar_motas():
    return 'Listagem de motas'


@app.route('/contatos')
def contatos():
    return 'Contatos'


@app.route('/carros')
def listar_carros():
    return 'Listagem de carros'


@app.route('/carros/<int:carro_id>')
def exibir_carro(carro_id):
    return f'Detalhes do carro {carro_id}'


# Rota para a página de login do administrador

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_logged_in' in session and session['admin_logged_in']:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Simulação do login do administrador
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas. Tente novamente.', 'danger')

    return render_template('admin_login.html', title='Admin Login')


# Rota para a página de administração após o login, adicionar veículos e processar o formulário de adição
@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        tipo = request.form['tipo']
        marca = request.form['marca']
        modelo = request.form['modelo']
        cor = request.form['cor']
        quilometragem = request.form['quilometragem']
        ano = request.form['ano']
        categoria = request.form['categoria']
        utilizacoes = request.form['utilizacoes']
        limite_utilizacoes = request.form['limite_utilizacoes']
        diaria = request.form['diaria']
        data_legalizacao = request.form['data_legalizacao']

        # Tratamento dos campos específicos para cada tipo de veículo
        if tipo == 'carro':
            potencia = request.form['potencia']
            transmissao = request.form['transmissao']
            veiculo = Carro(tipo=tipo, marca=marca, modelo=modelo, cor=cor, quilometragem=quilometragem,
                            ano=ano, categoria=categoria, utilizacoes=utilizacoes, limite_utilizacoes=limite_utilizacoes,
                            potencia=potencia, transmissao=transmissao, diaria=diaria,
                            data_legalizacao=datetime.strptime(data_legalizacao, '%Y-%m-%d').date())
        elif tipo == 'mota':
            cilindradas = request.form['cilindradas']
            peso = request.form['peso']
            veiculo = Mota(tipo=tipo, marca=marca, modelo=modelo, cor=cor, quilometragem=quilometragem,
                           ano=ano, categoria=categoria, utilizacoes=utilizacoes, limite_utilizacoes=limite_utilizacoes,
                           cilindradas=cilindradas, peso=peso, diaria=diaria,
                           data_legalizacao=datetime.strptime(data_legalizacao, '%Y-%m-%d').date())

        # Processar o upload das imagens
        imagens = request.files.getlist('imagens')
        imagens_paths = []
        for imagem in imagens:
            filename = secure_filename(imagem.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagem.save(path)
            imagens_paths.append(path)

        # Salvar os caminhos das imagens no veículo
        veiculo.imagens = ','.join(imagens_paths)

        db.session.add(veiculo)
        db.session.commit()

        flash('Veículo adicionado com sucesso!', 'success')

    return render_template('admin_dashboard.html', title='Admin Dashboard')


# Rota para fazer o logout do administrador
@app.route('/admin/logout')
def admin_logout():
    # Limpa a sessão do administrador
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('admin_login'))


# Execução da app
if __name__ == '__main__':
    # Define o diretório de upload de imagens (pasta 'static')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static')
    db.create_all()
    # Roda o servidor de desenvolvimento do Flask
    app.run(debug=True)
