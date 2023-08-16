import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pytz
from datetime import datetime, date, timedelta
import enum
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from werkzeug.utils import secure_filename


app = Flask(__name__)


# Definir a chave secreta para a sessão
app.secret_key = "sua_chave_secreta_aqui"

# Configurar o fuso horário de Portugal
app.config["TIMEZONE"] = pytz.timezone("Europe/Lisbon")

# Caminho do banco de dados
db_folder = os.path.join(os.path.dirname(__file__), "database")
db_path = os.path.join(db_folder, "database.db")

# Configurações do SQLite - banco de dados ficará dentro da pasta 'database'
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Defina o diretório de upload de imagens (pasta 'static')
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static/images")


# Configuração do Bootstrap 5 com Font Awesome
app.config["BOOTSTRAP_BOOTSWATCH_THEME"] = "yeti"
app.config["BOOTSTRAP_USE_MINIFIED"] = True
app.config["BOOTSTRAP_USE_CDN"] = True
app.config["BOOTSTRAP_FONTAWESOME"] = True

# Inicializar a extensão SQLAlchemy
db = SQLAlchemy(app)

# Configuração do Flask-Migrate
migrate = Migrate(app, db)


# Definir as opções válidas para o campo 'type' (Carro e Mota)
class VehicleType(enum.Enum):
    CARRO = "Carro"
    MOTA = "Mota"


# Classe para o modelo de Veículo
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(VehicleType), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    status = db.Column(db.Boolean, default=True)
    categoria = db.Column(db.String(50), nullable=False, default="")
    in_maintenance = db.Column(db.Boolean, default=False)
    last_maintenance_date = db.Column(db.Date)
    next_maintenance_date = db.Column(db.Date)
    maintenance_history = db.Column(db.String(1000), default="")
    last_legalization_date = db.Column(db.Date)
    next_legalization_date = db.Column(db.Date)
    legalization_history = db.Column(db.String(1000), default="")
    imagens = db.Column(db.String(1000))
    available_from = db.Column(db.Date, nullable=True)
    num_uses = db.Column(db.Integer, default=0)
    max_uses_before_maintenance = db.Column(db.Integer, default=50)

    def __init__(self, type, brand, model, year, price_per_day, categoria=""):
        self.type = type
        self.brand = brand
        self.model = model
        self.year = year
        self.price_per_day = price_per_day
        self.categoria = categoria
        self.maintenance_history = ""
        self.last_legalization_date = None
        self.next_legalization_date = None
        self.legalization_history = ""
        self.imagens = ""

    def update_categoria(self):
        if self.price_per_day <= 50:
            self.categoria = "Económico"
        elif self.price_per_day <= 250:
            self.categoria = "Silver"
        else:
            self.categoria = "Gold"

    def initialize_vehicle(self):
        # Define a data de criação do veículo como a data de última legalização
        self.last_legalization_date = date.today()

        # Calcular a data da próxima legalização (1 ano à frente)
        one_year_later = date.today() + timedelta(days=365)
        self.next_legalization_date = one_year_later

        # Atualizar a categoria do veículo com base no preço por dia
        if self.price_per_day >= 250:
            self.categoria = "Gold"
        elif self.price_per_day >= 50:
            self.categoria = "Silver"
        else:
            self.categoria = "Económico"

        # Definir as datas de manutenção
        self.last_maintenance_date = datetime.now().date()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)
        # Define a disponibilidade como hoje por padrão
        self.available_from = date.today()

    def start_maintenance(self):
        self.in_maintenance = True
        self.status = False
        self.last_maintenance_date = date.today()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=30)

    def end_maintenance(self):
        self.in_maintenance = False
        self.status = True
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)


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
    categoria = db.Column(db.String(20), nullable=False, default="Económico")

    def __init__(
        self,
        nome,
        apelido,
        email,
        telefone,
        data_nascimento,
        morada,
        nif,
        password,
        categoria,
    ):
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
        return f"<Cliente {self.nome} {self.apelido}>"


# Rota inicial
@app.route("/")
def index():
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    # Consultar todos os veículos disponíveis no banco de dados
    veiculos = Vehicle.query.filter_by(status=1).all()

    # Separar os veículos em carros e motas
    veiculos_carros = [
        veiculo for veiculo in veiculos if veiculo.type == VehicleType.CARRO
    ]
    veiculos_motas = [
        veiculo for veiculo in veiculos if veiculo.type == VehicleType.MOTA
    ]

    # Verificar se há uma sessão ativa de cliente
    if "client" in session:
        cliente = session["client"]
    else:
        cliente = None

    return render_template(
        "index.html",
        veiculos=veiculos,
        cliente=cliente,
        veiculos_carros=veiculos_carros,
        veiculos_motas=veiculos_motas,
        current_year=datetime.now().year,
    )


# Rota para a página de detalhes do veículo
@app.route("/vehicle/<int:id>")
def vehicle_details(id):
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    # Consultar o veículo pelo ID no banco de dados
    veiculo = Vehicle.query.get_or_404(id)

    return render_template("vehicle_details.html", veiculo=veiculo)


# Rota para a Reserva do veículo
def add_to_cart():
    veiculo = Vehicle.query.get_or_404(id)

    return render_template("add_to_cart.html", veiculo=veiculo)


# Rota para a Aluguel do veículo
def checkout():
    veiculo = Vehicle.query.get_or_404(id)

    return render_template("checkout.html", veiculo=veiculo)


# Função de middleware para verificar a sessão de administrador
@app.before_request
def check_admin_session():
    # Lista de rotas que requerem autenticação de administrador
    admin_routes = ["/admin", "/add_vehicle", "/edit_vehicle/", "/delete_vehicle/"]

    if request.path in admin_routes:
        if "admin" not in session:
            return redirect(url_for("login"))


# Rota para a página de login do administrador
@app.route("/login", methods=["GET", "POST"])
def login():
    # Verifica se já há uma sessão de admin ativa
    if "admin" in session:
        return redirect(url_for("admin_panel"))

    # Administradores temporários (em um projeto real, deve ser armazenado de forma segura)
    admins = {"admin": "password"}

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in admins and admins[username] == password:
            # Definir a sessão de administrador como ativa
            session["admin"] = True
            return redirect(url_for("admin_panel"))

    return render_template("login.html")


# Rota para o painel de administração
@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    if request.method == "POST":
        # Obter dados do formulário e adicionar um novo veículo
        # Restante do código...

        # Exibir uma mensagem flash de sucesso após adicionar o veículo
        flash("Novo veículo adicionado com sucesso!", "success")
        return redirect(url_for("admin_panel"))

    # Consultar todos os veículos no banco de dados
    vehicles = Vehicle.query.all()
    # Lógica para verificar veículos que precisam de manutenção
    today = date.today()
    vehicles_needing_maintenance = [
        vehicle
        for vehicle in vehicles
        if vehicle.next_maintenance_date
        and vehicle.next_maintenance_date <= (today + timedelta(days=30))
        and not vehicle.in_maintenance
    ]
    if vehicles_needing_maintenance:
        # Montar a mensagem de alerta
        alert_message = "Atenção: Os seguintes veículos precisam de manutenção:\n"
        for vehicle in vehicles_needing_maintenance:
            alert_message += f"{vehicle.brand} {vehicle.model} ({vehicle.type.value})\n"

        # Enviar a mensagem de alerta para a página usando a função flash
        flash(alert_message, "warning")

    # Lógica para verificar veículos que precisam de legalização
    vehicles_needing_legalization = [
        vehicle
        for vehicle in vehicles
        if vehicle.next_legalization_date
        and (vehicle.next_legalization_date - today).days <= 30
        and not vehicle.in_maintenance
    ]
    if vehicles_needing_legalization:
        # Montar a mensagem de alerta
        alert_message = "Atenção: Os seguintes veículos precisam de legalização:\n"
        for vehicle in vehicles_needing_legalization:
            alert_message += f'{vehicle.brand} {vehicle.model} ({vehicle.type.value}) - Próxima Legalização: {vehicle.next_legalization_date.strftime("%d/%m/%Y")}\n'

        # Enviar a mensagem de alerta para a página usando a função flash
        flash(alert_message, "warning")

    # Verificar se a data de próxima legalização é None e, se for, atribuir uma data futura
    for vehicle in vehicles:
        if not vehicle.next_legalization_date:
            vehicle.next_legalization_date = date.today() + timedelta(days=365)

    # Verificar se há veículos suficientes no estoque
    num_veiculos = len(vehicles)
    num_clientes = len(Cliente.query.all())
    estoque_suficiente = num_veiculos >= num_clientes + 5

    # sempre que a página inicial for carregada, ela verificará se há veículos suficientes no estoque e exibirá uma mensagem de aviso caso contrário.
    if not estoque_suficiente:
        flash(
            "Atenção: O estoque de veículos está baixo. Considere adicionar mais veículos para atender à demanda.",
            "warning",
        )

    # Passar a variável 'date' para o template 'admin.html'
    return render_template(
        "admin.html",
        vehicles=vehicles,
        date=date.today(),
        estoque_suficiente=estoque_suficiente,
    )


# Rota para a página de visualizar veículos


# Rota para visualisar os detalhes do veículo
@app.route("/admin/view_vehicle/<int:id>")
def view_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    imagens_paths = vehicle.imagens.split(",") if vehicle.imagens else []
    return render_template(
        "view_vehicle.html", vehicle=vehicle, imagens_paths=imagens_paths
    )


# Rota para a página de adicionar veículos
@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    if request.method == "POST":
        # Obter dados do formulário
        type = request.form["vehicle-type"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = int(request.form["year"])
        price_per_day = float(request.form["price_per_day"])

        # Processar o upload das imagens
        imagens = request.files.getlist("imagens")
        imagens_paths = []
        for imagem in imagens:
            filename = secure_filename(imagem.filename)
            # Caminho relativo à pasta 'static'
            path = filename
            full_path = os.path.join(app.config["UPLOAD_FOLDER"], path)
            imagem.save(full_path)
            imagens_paths.append(path)

        # Criar um novo objeto Veiculo e adicioná-lo ao banco de dados
        novo_veiculo = Vehicle(
            type=VehicleType[type.upper()],
            brand=brand,
            model=model,
            year=year,
            price_per_day=price_per_day,
        )
        # Salvar os caminhos das imagens
        novo_veiculo.imagens = ",".join(imagens_paths).lstrip("").lstrip(",")
        novo_veiculo.initialize_vehicle()
        db.session.add(novo_veiculo)
        db.session.commit()  # Salvar o novo veículo no banco de dados

        # Redirecionar para o painel de administração com mensagem de sucesso
        flash("Novo veículo adicionado com sucesso!", "success")
        return redirect(url_for("admin_panel"))

    return render_template("add_vehicle.html")


# Rota para a página de edição de veículo
@app.route("/edit_vehicle/<int:id>", methods=["GET", "POST"])
def edit_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    if request.method == "POST":
        # Obter os dados do formulário
        type = request.form["vehicle_type"]
        brand = request.form["brand"]
        model = request.form["model"]
        year = int(request.form["year"])
        price_per_day = float(request.form["price_per_day"])
        last_maintenance_date_str = request.form["last_maintenance_date"]
        next_maintenance_date_str = request.form["next_maintenance_date"]
        last_legalization_date_str = request.form["last_legalization_date"]
        next_legalization_date_str = request.form["next_legalization_date"]
        available_from_str = request.form["available_from"]
        max_uses_before_maintenance = int(request.form["max_uses_before_maintenance"])

        # Converter as datas do formulário em objetos date
        vehicle.last_maintenance_date = datetime.strptime(
            last_maintenance_date_str, "%Y-%m-%d"
        ).date()
        vehicle.next_maintenance_date = datetime.strptime(
            next_maintenance_date_str, "%Y-%m-%d"
        ).date()
        vehicle.last_legalization_date = datetime.strptime(
            last_legalization_date_str, "%Y-%m-%d"
        ).date()
        vehicle.next_legalization_date = datetime.strptime(
            next_legalization_date_str, "%Y-%m-%d"
        ).date()
        vehicle.available_from = datetime.strptime(
            available_from_str, "%Y-%m-%d"
        ).date()

        # Atualizar a categoria do veículo com base no novo preço por dia
        if price_per_day <= 50:
            vehicle.categoria = "Económico"
        elif price_per_day <= 250:
            vehicle.categoria = "Silver"
        else:
            vehicle.categoria = "Gold"

        # Processar o upload das imagens
        imagens = request.files.getlist("imagens")
        imagens_paths = vehicle.imagens.split(",")

        for imagem in imagens:
            if imagem.filename == "":
                # A imagem está vazia, ignorá-la
                continue

            filename = secure_filename(imagem.filename)
            # Caminho relativo à pasta 'static'
            path = filename
            full_path = os.path.join(app.config["UPLOAD_FOLDER"], path)
            imagem.save(full_path)
            imagens_paths.append(path)

        # Atualizar os dados do veículo
        vehicle.type = VehicleType[type.upper()]
        vehicle.brand = brand
        vehicle.model = model
        vehicle.year = year
        vehicle.price_per_day = price_per_day
        vehicle.max_uses_before_maintenance = max_uses_before_maintenance

        # Salvar os caminhos das imagens
        vehicle.imagens = ",".join(imagens_paths).lstrip("").lstrip(",")
        db.session.commit()

        # Redirecionar de volta para o painel de administração
        flash("Veículo atualizado com sucesso!", "success")
        return redirect(url_for("admin_panel"))

    # Renderizar a página de edição de veículo com o formulário preenchido
    return render_template(
        "edit_vehicle.html", vehicle=vehicle, VehicleType=VehicleType
    )


# Rota para exclusão de veículo
@app.route("/delete_vehicle/<int:id>", methods=["POST"])
def delete_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    # Remover o veículo do banco de dados
    db.session.delete(vehicle)
    db.session.commit()

    return redirect(url_for("admin_panel"))


# Rota para exclusão de imagem
@app.route("/delete_image/<path:image_path>/<int:vehicle_id>", methods=["POST"])
def delete_image(image_path, vehicle_id):
    # Encontrar o veículo no banco de dados pelo ID
    vehicle = Vehicle.query.get(vehicle_id)
    if not vehicle:
        flash("Veículo não encontrado.", "error")
        return redirect(url_for("edit_vehicle", id=vehicle_id))

    if request.method == "POST" or request.form.get("_method") == "DELETE":
        # Verificar se a imagem está associada ao veículo
        if image_path in vehicle.imagens.split(","):
            # Remover a imagem do servidor
            try:
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], image_path))
            except Exception as e:
                flash(
                    "Imagem não existe na base de dados, então foi atualizado a lista e removida a imagem não existente!",
                    "warning",
                )

            # Atualizar o registro do veículo no banco de dados para refletir a remoção da imagem
            imagens = vehicle.imagens.split(",")
            imagens.remove(image_path)
            vehicle.imagens = ",".join(imagens).lstrip("").lstrip(",")

            # Salvar as alterações no banco de dados
            db.session.commit()

            flash("Imagem removida com sucesso!", "success")

        return redirect(url_for("edit_vehicle", id=vehicle_id))

    else:
        flash("Método de requisição inválido.", "error")
        return redirect(url_for("edit_vehicle", id=vehicle_id))


# Rota para a página de login do cliente
@app.route("/client_login", methods=["GET", "POST"])
def client_login():
    if "client" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Consulta todos os clientes existentes no banco de dados
        clientes = Cliente.query.all()

        # Verifica se as credenciais de login estão corretas
        for cliente in clientes:
            if cliente.email == email and cliente.password == password:
                # Define a sessão do cliente logado
                session["client"] = {
                    "id": cliente.id,
                    "nome": cliente.nome,
                    "email": cliente.email,
                }

                # Exibe a mensagem de sucesso na página de login do cliente
                success_message = "Cliente logado com sucesso!"
                return redirect(url_for("index"))

        # Se as credenciais estiverem incorretas, exibe uma mensagem de erro
        error_message = "Credenciais de login inválidas. Por favor, tente novamente."
        return render_template("client_login.html", error_message=error_message)

    return render_template("client_login.html")


# Rota para logout do cliente
@app.route("/client_logout")
def client_logout():
    session.pop("client", None)  # Remove a chave 'client' da sessão
    # Redireciona para a página de login do cliente
    return redirect(url_for("client_login"))


# Rota para logout
@app.route("/logout")
def logout():
    # Remover a sessão de administrador
    session.pop("admin", None)
    return redirect(url_for("login"))


# Rota para a página de registro do cliente
@app.route("/register_client", methods=["GET", "POST"])
def register_client():
    if "client" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        nome = request.form["nome"]
        apelido = request.form["apelido"]
        email = request.form["email"]
        telefone = request.form["telefone"]
        data_nascimento = datetime.strptime(
            request.form["data_nascimento"], "%Y-%m-%d"
        ).date()
        morada = request.form["morada"]
        nif = request.form["nif"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        price_per_day = float(request.form["price_per_day"])

        # Verifica se as senhas coincidem
        if password != confirm_password:
            error_message = "As senhas não coincidem. Por favor, tente novamente."
            return render_template("register_client.html", error_message=error_message)

        # Verifica se a senha atende aos requisitos mínimos (8 caracteres entre letras e números)
        if (
            len(password) < 8
            or not any(char.isdigit() for char in password)
            and not any(char.isalpha() for char in password)
        ):
            error_message = "A senha deve conter no mínimo 8 caracteres, entre letras e números. Por favor, tente novamente."
            return render_template("register_client.html", error_message=error_message)

        # Define a categoria do cliente com base na diária escolhida
        if price_per_day >= 250:
            categoria = "Gold"
        elif price_per_day >= 50:
            categoria = "Silver"
        else:
            categoria = "Económico"

        # Cria um novo objeto Cliente e adiciona ao banco de dados
        novo_cliente = Cliente(
            nome=nome,
            apelido=apelido,
            email=email,
            telefone=telefone,
            data_nascimento=data_nascimento,
            morada=morada,
            nif=nif,
            password=password,
            categoria=categoria,
        )
        db.session.add(novo_cliente)
        db.session.commit()  # Salva o novo cliente no banco de dados

        # Redireciona para a página de login do cliente
        return redirect(url_for("client_login"))

    return render_template("register_client.html")


# Rota para confirmar a legalização do veículo
@app.route("/legalize_vehicle/<int:id>", methods=["POST"])
def legalize_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    # Atualizar a data da última legalização
    vehicle.last_legalization_date = date.today()

    # Atualizar a data da próxima legalização (1 ano após a última legalização)
    vehicle.next_legalization_date = vehicle.last_legalization_date + timedelta(
        days=365
    )

    # Salvar o histórico de legalizações
    vehicle.legalization_history += (
        f'Legalização realizada {vehicle.last_legalization_date.strftime("%Y-%m-%d")};'
    )

    # Salvar as alterações no banco de dados
    db.session.commit()

    # Exibir mensagem flash informando que o veículo foi legalizado
    flash("Veículo legalizado com sucesso!", "info")

    return redirect(url_for("admin_panel"))


# Rota para manutenção do veículo
@app.route("/admin/maintenance_vehicle/<int:id>", methods=["GET", "POST"])
def maintenance_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)

    if request.method == "POST":
        # Verificar se o botão de manutenção foi pressionado
        if "maintenance" in request.form:
            # Atualizar o status do veículo para indisponível, definir a data de manutenção e a próxima manutenção
            vehicle.status = False
            vehicle.in_maintenance = True
            vehicle.last_maintenance_date = date.today()
            vehicle.next_maintenance_date = date.today() + timedelta(
                days=6 * 30
            )  # Próxima manutenção em 6 meses
            # Atualizar histórico de manutenção
            vehicle.maintenance_history += f'Manutenção iniciada {vehicle.last_maintenance_date.strftime("%Y-%m-%d")};'

            db.session.commit()

            # Adicionar mensagem flash para informar que o veículo está em manutenção
            flash("Veículo enviado para manutenção com sucesso!", "success")

        # Verificar se o botão de concluir manutenção foi pressionado
        elif "complete_maintenance" in request.form:
            # Atualizar o status do veículo para disponível, definir in_maintenance como False
            vehicle.status = True
            vehicle.in_maintenance = False

            # Atualizar a próxima data de manutenção (180 dias após a última manutenção)
            vehicle.next_maintenance_date = vehicle.last_maintenance_date + timedelta(
                days=180
            )
            # Atualizar histórico de manutenção
            vehicle.maintenance_history += f'Manutenção concluída {vehicle.last_maintenance_date.strftime("%Y-%m-%d")};'

            db.session.commit()

            # Adicionar mensagem flash para informar sobre a conclusão da manutenção
            flash("Veículo concluiu a manutenção com sucesso!", "success")

        return redirect(url_for("admin_panel"))

    return render_template("maintenance_vehicle.html", vehicle=vehicle)


# Função para verificar o status de manutenção do veículo
def check_maintenance_status():
    # Obter todos os veículos em manutenção
    vehicles_in_maintenance = Vehicle.query.filter_by(in_maintenance=True).all()

    # Verificar se a data atual é igual ou superior à data de próxima manutenção
    today = date.today()
    for vehicle in vehicles_in_maintenance:
        if vehicle.next_maintenance_date and vehicle.next_maintenance_date <= today:
            # Definir o veículo como disponível e definir in_maintenance como False
            vehicle.status = True
            vehicle.in_maintenance = False
            vehicle.next_maintenance_date = vehicle.last_maintenance_date + timedelta(
                days=180
            )
            db.session.commit()


# Função para registrar uma nova utilização do veículo e verificar a próxima manutenção
def register_usage(vehicle):
    vehicle.num_uses += 1

    if vehicle.num_uses >= vehicle.max_uses_before_maintenance:
        days_since_last_maintenance = (
            datetime.now().date() - vehicle.last_maintenance_date
        ).days
        if days_since_last_maintenance >= 30:
            vehicle.next_maintenance_date = vehicle.last_maintenance_date + timedelta(
                days=30
            )

    db.session.commit()


# Rota para atualizar o número de utilização do veículo
@app.route("/register_usage/<int:vehicle_id>", methods=["POST"])
def register_usage_route(vehicle_id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Registrar a utilização e verificar a próxima manutenção
    register_usage(vehicle)

    # Redirecionar de volta para a página de edição do veículo
    flash("Utilização registrada com sucesso!", "success")
    return redirect(url_for("edit_vehicle", id=vehicle_id))


# Criar um scheduler para executar tarefas em segundo plano
scheduler = BackgroundScheduler()
scheduler.start()

# Agendar a função para ser executada diariamente à meia-noite (00:00)
scheduler.add_job(
    check_maintenance_status, "interval", days=1, start_date="2023-07-27 00:00:00"
)

# Ao sair da aplicação, finalizar o scheduler
atexit.register(lambda: scheduler.shutdown())

# Verificar e criar o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)


# Se a pasta 'static/images' não existir, crie-a
if not os.path.exists(os.path.join(app.root_path, "static/images")):
    os.makedirs(os.path.join(app.root_path, "static/images"))

# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == "__main__":
    app.run(debug=True)
