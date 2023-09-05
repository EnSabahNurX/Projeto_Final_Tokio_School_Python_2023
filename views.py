from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, session, flash
from models import db, Veiculo, VehicleType, Cliente, Reservation, Categoria
from app import app
from admin_views import check_maintenance_status, register_usage
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)

# Configuração do Flask Login
login_manager = LoginManager(app)
login_manager.login_view = "client_login"


@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(int(user_id))


def index():
    """
    Rota da página inicial.
    """
    check_maintenance_status()

    data_inicio = request.args.get("data_inicio")
    data_entrega = request.args.get("data_entrega")
    categoria = request.args.get("categoria", "all")

    if current_user.is_authenticated:
        if categoria == "all":
            categoria = current_user.categoria

    if categoria == "all":
        veiculos = Veiculo.query.filter_by(status=1).all()
    else:
        veiculos = (
            Veiculo.query.join(Categoria)
            .filter(Categoria.nome == categoria, Veiculo.status == 1)
            .all()
        )

    if not data_inicio:
        data_inicio = date.today()
    else:
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date()

    if not data_entrega:
        data_entrega = date.today() + timedelta(days=1)
    else:
        data_entrega = datetime.strptime(data_entrega, "%Y-%m-%d").date()

    if data_inicio < date.today():
        flash("A data de início não pode ser no passado.", "danger")
        return redirect(url_for("index"))

    if data_inicio >= data_entrega:
        flash("A data de início deve ser anterior à data de entrega.", "danger")
        return redirect(url_for("index"))

    veiculos = [
        veiculo
        for veiculo in veiculos
        if is_vehicle_available(veiculo, data_inicio, data_entrega)
    ]

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
        data_inicio=data_inicio,
        data_entrega=data_entrega,
    )


def is_vehicle_available(veiculo, data_inicio, data_entrega):
    """
    Verifica se um veículo está disponível durante um período selecionado.
    """
    if veiculo.in_maintenance:
        return False

    data_inicio_datetime = datetime.combine(data_inicio, datetime.min.time())
    data_entrega_datetime = datetime.combine(data_entrega, datetime.max.time())

    reservas_conflitantes = Reservation.query.filter(
        Reservation.vehicle_id == veiculo.id,
        Reservation.status == "Ativa",
        Reservation.start_date <= data_entrega_datetime,
        Reservation.end_date >= data_inicio_datetime,
    ).all()

    if reservas_conflitantes:
        return False

    return True


def vehicle_details(id):
    """
    Rota da página de detalhes do veículo.
    """
    check_maintenance_status()
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


@login_required
def reserve(id):
    """
    Rota da página de reserva do veículo.
    """
    veiculo = Veiculo.query.get(id)

    if request.method == "POST":
        data_recolha = request.form.get("data_recolha")
        hora_recolha = request.form.get("hora_recolha")
        duracao = int(request.form.get("duracao"))
        payment_method = request.form.get("payment_method")
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

    return render_template("reserve.html", veiculo=veiculo)


def complete_payment():
    """
    Rota para processar o pagamento.
    """
    veiculo_id = request.form.get("veiculo_id")
    data_recolha = request.form.get("data_recolha")
    hora_recolha = request.form.get("hora_recolha")
    duracao = int(request.form.get("duracao"))
    payment_method = request.form.get("payment_method")

    if (
        request.form.get("duracao") is not None
        and request.form.get("duracao").isdigit()
    ):
        duracao = int(request.form.get("duracao"))
    else:
        return render_template("payment_error.html", message="Duração inválida")

    veiculo = Veiculo.query.get(veiculo_id)
    preco_total = duracao * veiculo.price_per_day

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

    payment_response = payment_responses.get(payment_method)

    if payment_response:
        if payment_response["success"]:
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
            return render_template(
                "payment_error.html", message=payment_response["message"]
            )
    else:
        return render_template(
            "payment_error.html", message="Método de pagamento inválido"
        )


def order_confirmation():
    """
    Rota para a página de confirmação de pagamento.
    """
    return render_template("order_confirmation.html")


def client_login():
    """
    Rota para a página de login do cliente.
    """
    if current_user.is_authenticated:
        redirect_url = session.pop("redirect_url", url_for("index"))
        return redirect(redirect_url)

    next_url = request.args.get("next") or url_for("index")

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        client = Cliente.query.filter_by(email=email).first()

        if client and client.email == email and client.password == password:
            login_user(client)
            flash("Login bem-sucedido!", "success")
            redirect_url = session.pop("redirect_url", url_for("index"))
            return redirect(next_url)

        error_message = "Credenciais de login inválidas. Por favor, tente novamente."
        return render_template(
            "client_login.html", error_message=error_message, next_url=next_url
        )

    return render_template("client_login.html", next_url=next_url)


def client_logout():
    """
    Rota para logout do cliente.
    """
    logout_user()
    return redirect(url_for("client_login"))


def register_client():
    """
    Rota para a página de registro do cliente.
    """
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

        if password != confirm_password:
            error_message = "As senhas não coincidem. Por favor, tente novamente."
            return render_template("register_client.html", error_message=error_message)

        if (
            len(password) < 8
            or not any(char.isdigit() for char in password)
            and not any(char.isalpha() for char in password)
        ):
            error_message = "A senha deve conter no mínimo 8 caracteres, entre letras e números. Por favor, tente novamente."
            return render_template("register_client.html", error_message=error_message)

        if price_per_day > 250:
            categoria = "Gold"
        elif price_per_day <= 50:
            categoria = "Económico"
        else:
            categoria = "Silver"

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
        db.session.commit()

        return redirect(url_for("client_login"))

    return render_template("register_client.html")


@login_required
def client_reservations():
    """
    Rota para visualizar as reservas do cliente.
    """
    Reservation.update_completed_reservations()
    customer_id = current_user.id
    future_reservations = (
        Reservation.query.filter(
            Reservation.customer_id == customer_id,
            Reservation.start_date >= date.today(),
        )
        .order_by(Reservation.start_date)
        .all()
    )

    past_reservations = (
        Reservation.query.filter(
            Reservation.customer_id == customer_id,
            Reservation.start_date < date.today(),
        )
        .order_by(Reservation.start_date.desc())
        .all()
    )

    return render_template(
        "client_reservations.html",
        future_reservations=future_reservations,
        past_reservations=past_reservations,
    )


@login_required
def cancel_reservation(id):
    """
    Rota para cancelar uma reserva do cliente.
    """
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
    """
    Rota para a página de edição de dados do cliente.
    """
    return render_template("edit_client.html")


@login_required
def update_client():
    """
    Rota para atualizar os dados do cliente.
    """
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
