import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instância do Flask
app = Flask(__name__)

# Verifica se a pasta "database" existe e, se não existir, cria-a
database_dir = os.path.join(app.root_path, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Configuração do URI do banco de dados SQLite
db_path = os.path.join(database_dir, 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Instância do SQLAlchemy
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
    disponibilidades = db.relationship('Disponibilidade', backref='mota', lazy=True)

class Disponibilidade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date)
    carro_id = db.Column(db.Integer, db.ForeignKey('carro.id'))
    mota_id = db.Column(db.Integer, db.ForeignKey('mota.id'))

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
