from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, session, flash
from models import db, Veiculo, VehicleType, Cliente, Reservation, Categoria
from app import app
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)

# COnfiguração do Flask Login
login_manager = LoginManager(app)
login_manager.login_view = "client_login"


# Função para verificar o status de manutenção do veículo
def check_maintenance_status():
    # Obter todos os veículos em manutenção
    vehicles_in_maintenance = Veiculo.query.filter_by(in_maintenance=True).all()

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


@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(int(user_id))


def index():
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    # Atribui a categoria padrão para os veículos exibidos na tela inicial sem cliente logado
    categoria = request.args.get("categoria", "all")

    # Cliente logado por padrão a categoria do cadastro
    if current_user.is_authenticated:
        if categoria == "all":
            categoria = current_user.categoria

    # Consultar todos os veículos disponíveis no banco de dados conforme a categoria do filtro selecionada
    if categoria == "all":
        veiculos = Veiculo.query.filter_by(status=1).all()
    else:
        veiculos = (
            Veiculo.query.join(Categoria)
            .filter(Categoria.nome == categoria, Veiculo.status == 1)
            .all()
        )

    # Separar os veículos em carros e motas
    veiculos_carros = [
        veiculo for veiculo in veiculos if veiculo.type == VehicleType.CARRO
    ]
    veiculos_motas = [
        veiculo for veiculo in veiculos if veiculo.type == VehicleType.MOTA
    ]

    return render_template(
        "index.html",
        veiculos=veiculos,
        veiculos_carros=veiculos_carros,
        veiculos_motas=veiculos_motas,
        current_year=datetime.now().year,
        categoria=categoria,
    )


def vehicle_details(id):
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    # Consultar o veículo pelo ID no banco de dados
    veiculo = Veiculo.query.get_or_404(id)
    image_paths = veiculo.imagens.split(",")
    images_with_index = [
        {"index": index, "path": path} for index, path in enumerate(image_paths)
    ]

    return render_template(
        "vehicle_details.html",
        veiculo=veiculo,
        images_with_index=images_with_index,
    )


# Decorador para verificar o login do cliente
@login_required
def reserve(id):
    # Obter o veículo a partir do ID
    veiculo = Veiculo.query.get(id)

    if request.method == "POST":
        # Receber os dados do formulário
        data_recolha = request.form.get("data_recolha")
        hora_recolha = request.form.get("hora_recolha")
        duracao = int(request.form.get("duracao"))
        payment_method = request.form.get("payment_method")

        # Calcular o preço total do aluguer
        preco_total = duracao * veiculo.price_per_day

        return render_template(
            "payment_simulation.html",
            veiculo=veiculo,
            data_recolha=data_recolha,
            hora_recolha=hora_recolha,
            duracao=duracao,
            preco_total=preco_total,
            payment_method=payment_method,
        )

    return render_template(
        "reserve.html",
        veiculo=veiculo,
    )


def complete_payment():
    # Receber os dados do formulário
    veiculo_id = request.form.get("veiculo_id")
    data_recolha = request.form.get("data_recolha")
    hora_recolha = request.form.get("hora_recolha")
    duracao = int(request.form.get("duracao"))
    payment_method = request.form.get("payment_method")

    # Verificar se a duração é um valor válido antes de convertê-lo em um inteiro
    if (
        request.form.get("duracao") is not None
        and request.form.get("duracao").isdigit()
    ):
        duracao = int(request.form.get("duracao"))
    else:
        # Lidar com o caso em que a duração não é um número válido
        return render_template("payment_error.html", message="Duração inválida")

    # Obter o veículo a partir do ID
    veiculo = Veiculo.query.get(veiculo_id)

    # Calcular o preço total do aluguer
    preco_total = duracao * veiculo.price_per_day

    # Dicionário para simular as respostas de pagamento
    payment_responses = {
        "mbway": {
            "success": True,
            "message": "Pagamento com MB WAY realizado com sucesso!",
        },
        "multibanco": {
            "success": True,
            "message": "Pagamento com Multibanco realizado com sucesso!",
            "entidade": "12345",
            "referencia": "67890",
        },
    }

    # Obter a resposta de pagamento do dicionário simulado
    payment_response = payment_responses.get(payment_method)

    if payment_response:
        if payment_response["success"]:
            # Simulação de sucesso no pagamento
            # Adicionar a reserva
            customer_id = int(current_user.id)
            reservation = Reservation(
                customer_id=customer_id,
                vehicle_id=veiculo_id,
                start_date=datetime.strptime(data_recolha, "%Y-%m-%d"),
                start_time=datetime.strptime(hora_recolha, "%H:%M").time(),
                end_date=datetime.strptime(data_recolha, "%Y-%m-%d")
                + timedelta(days=duracao),
                end_time=datetime.strptime(hora_recolha, "%H:%M").time(),
                duration=duracao,
                price=preco_total,
            )
            reservation.add_reservations()

            return redirect(url_for("order_confirmation"))
        else:
            # Simulação de falha no pagamento
            return render_template(
                "payment_error.html", message=payment_response["message"]
            )
    else:
        # Lidar com o caso em que o método de pagamento não é válido
        return render_template(
            "payment_error.html", message="Método de pagamento inválido"
        )


def order_confirmation():
    return render_template("order_confirmation.html")


def client_login():
    if current_user.is_authenticated:
        # Se o usuário já estiver logado, redirecione para a página de reserva
        # Verifica se há uma URL de redirecionamento armazenada
        redirect_url = session.pop("redirect_url", url_for("index"))
        return redirect(redirect_url)

    next_url = request.args.get("next") or url_for("index")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Verifique as credenciais do cliente aqui (substitua com a sua lógica)
        client = Cliente.query.filter_by(email=email).first()
        if client and client.email == email and client.password == password:
            # Define a sessão para o usuário logado
            login_user(client)
            flash("Login bem-sucedido!", "success")

            # Verifica se há uma URL de redirecionamento armazenada
            redirect_url = session.pop("redirect_url", url_for("index"))
            return redirect(next_url)

        # Em caso de credenciais inválidas, exiba uma mensagem de erro
        error_message = "Credenciais de login inválidas. Por favor, tente novamente."
        return render_template(
            "client_login.html",
            error_message=error_message,
            next_url=next_url,
        )

    return render_template(
        "client_login.html",
        next_url=next_url,
    )


def client_logout():
    logout_user()
    # Redireciona para a página de login do cliente
    return redirect(url_for("client_login"))


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
        if not str(nif).isdigit():
            error_message = (
                "O NIF deve conter apenas números. Por favor, tente novamente."
            )
            return render_template("register_client.html", error_message=error_message)

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
        if price_per_day > 250:
            categoria = "Gold"
        elif price_per_day <= 50:
            categoria = "Económico"
        else:
            categoria = "Silver"

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


# Decorador para verificar o login do cliente
@login_required
def client_reservations():
    Reservation.update_completed_reservations()
    customer_id = current_user.id
    future_reservations = Reservation.query.filter(
        Reservation.customer_id == customer_id, Reservation.start_date >= date.today()
    ).all()

    past_reservations = Reservation.query.filter(
        Reservation.customer_id == customer_id, Reservation.start_date < date.today()
    ).all()

    return render_template(
        "client_reservations.html",
        future_reservations=future_reservations,
        past_reservations=past_reservations,
    )


@login_required
def cancel_reservation(id):
    reservation = Reservation.query.get(id)
    if reservation:
        reservation.status = "Cancelada"
        db.session.commit()
        flash("Reserva cancelada com sucesso!", "success")
    else:
        flash("Reserva não encontrada.", "danger")

    return redirect(url_for("client_reservations"))


@login_required
def edit_client():
    return render_template("edit_client.html")


@login_required
def update_client():
    new_nome = request.form.get("nome")
    new_apelido = request.form.get("apelido")
    new_email = request.form.get("email")
    new_telefone = request.form.get("telefone")
    new_data_nascimento = request.form.get("data_nascimento")
    new_morada = request.form.get("morada")
    new_nif = request.form.get("nif")
    new_price_per_day = float(request.form["price_per_day"])
    new_password = request.form.get("password")

    if (
        new_nome
        and new_apelido
        and new_email
        and new_telefone
        and new_data_nascimento
        and new_morada
        and new_nif
        and new_price_per_day
    ):
        current_user.nome = new_nome
        current_user.apelido = new_apelido
        current_user.email = new_email
        current_user.telefone = new_telefone
        current_user.data_nascimento = datetime.strptime(
            new_data_nascimento, "%Y-%m-%d"
        ).date()
        current_user.morada = new_morada
        current_user.nif = new_nif
        current_user.price_per_day = new_price_per_day

        if new_password:
            current_user.password = new_password

        # Define a categoria do cliente com base na diária escolhida
        if new_price_per_day > 250:
            categoria = "Gold"
        elif new_price_per_day <= 50:
            categoria = "Económico"
        else:
            categoria = "Silver"
        current_user.categoria = categoria

        db.session.commit()
        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for("index"))
    else:
        flash("Por favor, preencha todos os campos obrigatórios.", "danger")

    return redirect(url_for("edit_client"))
