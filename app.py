import os
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pytz

app = Flask(__name__)

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


@app.route('/')
def home():
    return 'Luxury Wheels, aluguer de carros e motas'


@app.route('/carros')
def listar_carros():
    return 'Listagem de carros'


@app.route('/carros/<int:carro_id>')
def exibir_carro(carro_id):
    return f'Detalhes do carro {carro_id}'


# Execução da app
if __name__ == '__main__':
    # O debug=True faz com que cada vez que reiniciemos o servidor ou modifiquemos o código, o servidor de Flask reinicia-se sozinho
    app.run(debug=True)
