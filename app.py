import os
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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

# Definição dos modelos de dados
class Carro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    ano = db.Column(db.Integer)
    diaria = db.Column(db.Float)
    combustivel = db.Column(db.String(20))
    lugares = db.Column(db.Integer)
    potencia = db.Column(db.Integer)
    transmissao = db.Column(db.String(50))
    categoria = db.Column(db.String(50))
    utilizacoes = db.Column(db.Integer, default=0)
    limite_utilizacoes = db.Column(db.Integer)
    data_legalizacao = db.Column(db.Date)
    data_alerta_legalizacao = db.Column(db.Date)
    disponibilidades = db.relationship('Disponibilidade', backref='carro', lazy=True)

class Mota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50))
    modelo = db.Column(db.String(50))
    ano = db.Column(db.Integer)
    diaria = db.Column(db.Float)
    combustivel = db.Column(db.String(20))
    lugares = db.Column(db.Integer)
    cilindradas = db.Column(db.Integer)
    peso = db.Column(db.Float)
    categoria = db.Column(db.String(50))
    utilizacoes = db.Column(db.Integer, default=0)
    limite_utilizacoes = db.Column(db.Integer)
    data_legalizacao = db.Column(db.Date)
    data_alerta_legalizacao = db.Column(db.Date)
    disponibilidades = db.relationship('Disponibilidade', backref='mota', lazy=True)

class Disponibilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'))
    mota_id = db.Column(db.Integer, db.ForeignKey('mota.id'))

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
        data_alerta_legalizacao = data_legalizacao_portugal - timedelta(days=30)
        
        # Converte a data de alerta de volta para o formato local de Portugal
        target.data_alerta_legalizacao = data_alerta_legalizacao.date()



# Criação das tabelas do banco de dados
if not os.path.exists('database.db'):
    with app.app_context():
        db.create_all()
        #db.session.commit()
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

