import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pytz
import enum

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

# Definir as opções válidas para o campo 'type' (Carro e Mota)


class VehicleType(enum.Enum):
    CARRO = 'Carro'
    MOTA = 'Mota'


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(VehicleType), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"{self.brand} {self.model} ({self.year})"

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
    if request.method == 'POST':
        # Obter dados do formulário
        vehicle_id = request.form.get('id')
        type = request.form['type']
        brand = request.form['brand']
        model = request.form['model']
        year = int(request.form['year'])
        price_per_day = float(request.form['price_per_day'])

        # Verificar se é uma adição ou edição de veículo
        if vehicle_id:
            # Edição de veículo existente
            vehicle = Vehicle.query.get(vehicle_id)
            # Converter o valor para VehicleType
            vehicle.type = VehicleType[type.upper()]
            vehicle.brand = brand
            vehicle.model = model
            vehicle.year = year
            vehicle.price_per_day = price_per_day
        else:
            # Adição de novo veículo
            vehicle = Vehicle(type=VehicleType[type.upper(
            )], brand=brand, model=model, year=year, price_per_day=price_per_day)
            db.session.add(vehicle)

        # Salvar as alterações no banco de dados
        db.session.commit()

    # Consultar todos os veículos no banco de dados
    vehicles = Vehicle.query.all()
    return render_template('admin.html', vehicles=vehicles)


# Rota para a página de edição de veículo

@app.route('/edit_vehicle/<int:id>', methods=['GET', 'POST'])
def edit_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    if request.method == 'POST':
        # Obter dados do formulário
        type = request.form['type']
        brand = request.form['brand']
        model = request.form['model']
        year = int(request.form['year'])
        price_per_day = float(request.form['price_per_day'])

        # Atualizar os dados do veículo
        # Converter o valor para VehicleType
        vehicle.type = VehicleType[type.upper()]
        vehicle.brand = brand
        vehicle.model = model
        vehicle.year = year
        vehicle.price_per_day = price_per_day

        # Salvar as alterações no banco de dados
        db.session.commit()

        # Redirecionar de volta para o painel de administração
        return redirect(url_for('admin_panel'))

    # Renderizar a página de edição de veículo com o formulário preenchido
    return render_template('edit_vehicle.html', vehicle=vehicle)

# Rota para exclusão de veículo


@app.route('/delete_vehicle/<int:id>', methods=['POST'])
def delete_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    # Remover o veículo do banco de dados
    db.session.delete(vehicle)
    db.session.commit()

    return redirect(url_for('admin_panel'))


# Verificar e criar o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == '__main__':
    app.run(debug=True)
