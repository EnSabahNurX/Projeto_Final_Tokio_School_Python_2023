import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pytz
import datetime
import enum

app = Flask(__name__)

# Definir a chave secreta para a sessão
app.secret_key = 'sua_chave_secreta_aqui'

# Configurar o fuso horário de Portugal
app.config['TIMEZONE'] = pytz.timezone('Europe/Lisbon')

# Caminho do banco de dados
db_folder = os.path.join(os.path.dirname(__file__), 'database')
db_path = os.path.join(db_folder, 'database.db')

# Configurações do SQLite - banco de dados ficará dentro da pasta 'database'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do Bootstrap 5 com Font Awesome
app.config['BOOTSTRAP_BOOTSWATCH_THEME'] = 'yeti'
app.config['BOOTSTRAP_USE_MINIFIED'] = True
app.config['BOOTSTRAP_USE_CDN'] = True
app.config['BOOTSTRAP_FONTAWESOME'] = True

# Inicializar a extensão SQLAlchemy
db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)

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
    category = db.Column(db.String(20), nullable=False)
    daily_value = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"{self.brand} {self.model} ({self.year})"


# Modelo de classe para clientes
class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    apelido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    morada = db.Column(db.String(200), nullable=False)
    nif = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(20), nullable=False, default='Económico')

    def __init__(self, nome, apelido, email, telefone, data_nascimento, morada, nif, password, categoria):
        self.nome = nome
        self.apelido = apelido
        self.email = email
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.morada = morada
        self.nif = nif
        self.password = password
        self.categoria = categoria

    def __repr__(self):
        return f'<Cliente {self.nome} {self.apelido}>'


# Rota inicial
@app.route('/')
def index():
    # Carrega todos os veículos do banco de dados
    veiculos = Vehicle.query.all()

    # Verifica se há uma sessão ativa de cliente
    if 'client' in session:
        cliente = session['client']
    else:
        cliente = None

    return render_template('index.html', veiculos=veiculos, cliente=cliente)


# Função de middleware para verificar a sessão de administrador
@app.before_request
def check_admin_session():
    # Lista de rotas que requerem autenticação de administrador
    admin_routes = ['/admin', '/edit_vehicle/', '/delete_vehicle/']

    if request.path in admin_routes:
        if 'admin' not in session:
            return redirect(url_for('login'))


# Rota para a página de login do administrador
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Verifica se já há uma sessão de admin ativa
    if 'admin' in session:
        return redirect(url_for('admin_panel'))

    # Administradores temporários (em um projeto real, deve ser armazenado de forma segura)
    admins = {'admin': 'password'}

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admins and admins[username] == password:
            # Definir a sessão de administrador como ativa
            session['admin'] = True
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


# Rota para a página de login do cliente
@app.route('/client_login', methods=['GET', 'POST'])
def client_login():
    if 'client' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Consulta todos os clientes existentes no banco de dados
        clientes = Cliente.query.all()

        # Verifica se as credenciais de login estão corretas
        for cliente in clientes:
            if cliente.email == email and cliente.password == password:
                # Define a sessão do cliente logado
                session['client'] = {
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'email': cliente.email
                }

                # Exibe a mensagem de sucesso na página de login do cliente
                success_message = 'Cliente logado com sucesso!'
                return redirect(url_for('index'))

        # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
        error_message = 'Credenciais de login inválidas. Por favor, tente novamente.'
        return render_template('client_login.html', error_message=error_message)

    return render_template('client_login.html')

# Rota para logout do cliente


@app.route('/client_logout')
def client_logout():
    session.pop('client', None)  # Remove a chave 'client' da sessão
    # Redireciona para a página de login do cliente
    return redirect(url_for('client_login'))


# Rota para logout
@app.route('/logout')
def logout():
    # Remover a sessão de administrador
    session.pop('admin', None)
    return redirect(url_for('login'))


# Rota para a página de registro do cliente


@app.route('/register_client', methods=['GET', 'POST'])
def register_client():
    if 'client' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome']
        apelido = request.form['apelido']
        email = request.form['email']
        telefone = request.form['telefone']
        data_nascimento = datetime.datetime.strptime(
            request.form['data_nascimento'], '%Y-%m-%d').date()
        morada = request.form['morada']
        nif = request.form['nif']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        price_per_day = float(request.form['price_per_day'])

        # Verifica se as senhas coincidem
        if password != confirm_password:
            error_message = 'As senhas não coincidem. Por favor, tente novamente.'
            return render_template('register_client.html', error_message=error_message)

        # Verifica se a senha atende aos requisitos mínimos (8 caracteres entre letras e números)
        if len(password) < 8 or not any(char.isdigit() for char in password) and not any(char.isalpha() for char in password):
            error_message = 'A senha deve conter no mínimo 8 caracteres, entre letras e números. Por favor, tente novamente.'
            return render_template('register_client.html', error_message=error_message)

        # Define a categoria do cliente com base na diária escolhida
        if price_per_day >= 250:
            categoria = 'Gold'
        elif price_per_day >= 50:
            categoria = 'Silver'
        else:
            categoria = 'Económico'

        # Cria um novo objeto Cliente e adiciona ao banco de dados
        novo_cliente = Cliente(nome=nome, apelido=apelido, email=email, telefone=telefone,
                               data_nascimento=data_nascimento, morada=morada, nif=nif, password=password, categoria=categoria)
        db.session.add(novo_cliente)
        db.session.commit()  # Salva o novo cliente no banco de dados

        # Redireciona para a página de login do cliente
        return redirect(url_for('client_login'))

    return render_template('register_client.html')


# Verificar e criar o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == '__main__':
    app.run(debug=True)
