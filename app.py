import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instância do Flask
app = Flask(__name__)

# URI do banco de dados SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'database.db')

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
    transmissao = db.Column(db.String(50))


# Criação das tabelas do banco de dados
if not os.path.exists('database.db'):
    with app.app_context():
        db.create_all()