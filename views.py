import os
from datetime import datetime, date, timedelta
from flask import render_template, request, redirect, url_for, session, flash
from models import db, Vehicle, VehicleType, Cliente
from decorators import login_required
from werkzeug.utils import secure_filename
from app import app


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


def vehicle_details(id):
    # Chamar a função para verificar a manutenção do veículo
    check_maintenance_status()

    # Consultar o veículo pelo ID no banco de dados
    veiculo = Vehicle.query.get_or_404(id)
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
    # Obter o veículo a partir do ID
    veiculo = Vehicle.query.get(id)

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
    print(request.form.get("duracao"))
    # duracao = int(request.form.get("duracao"))
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
    veiculo = Vehicle.query.get(veiculo_id)

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
            return redirect(url_for("order_confirmation"))
        else:
            # Simulação de falha no pagamento
            return render_template(
                "payment_error.html", message=payment_response["message"]
            )

    # Redirecionar para a página de confirmação do pedido
    return redirect(url_for("order_confirmation"))


def order_confirmation():
    return render_template("order_confirmation.html")


def check_admin_session():
    # Lista de rotas que requerem autenticação de administrador
    admin_routes = ["/admin", "/add_vehicle", "/edit_vehicle/", "/delete_vehicle/"]

    if request.path in admin_routes:
        if "admin" not in session:
            return redirect(url_for("login"))


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


def view_vehicle(id):
    vehicle = Vehicle.query.get_or_404(id)
    imagens_paths = vehicle.imagens.split(",") if vehicle.imagens else []
    return render_template(
        "view_vehicle.html",
        vehicle=vehicle,
        imagens_paths=imagens_paths,
    )


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

        # Validar o ano
        if not isinstance(request.form["year"], int):
            flash("O ano deve ser um número inteiro.", category="danger")
            return False

        # Validar a diária
        if float(request.form["price_per_day"]) <= 0:
            flash("A diária deve ser um número positivo.", category="danger")
            return False

        # Validar as datas de legalização
        if (
            request.form["last_legalization_date"]
            >= request.form["next_legalization_date"]
        ):
            flash(
                "A última data de legalização deve ser anterior à próxima data de legalização.",
                category="danger",
            )
            return False

        # Salvar o veículo
        novo_veiculo.initialize_vehicle()
        db.session.add(novo_veiculo)
        db.session.commit()  # Salvar o novo veículo no banco de dados

        # Redirecionar para o painel de administração com mensagem de sucesso
        flash("Novo veículo adicionado com sucesso!", "success")
        return redirect(url_for("admin_panel"))

    return render_template("add_vehicle.html")


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

        # Validar o ano
        if not isinstance(request.form["year"], int):
            flash("O ano deve ser um número inteiro.", category="danger")
            return False

        # Validar a diária
        if float(request.form["price_per_day"]) <= 0:
            flash("A diária deve ser um número positivo.", category="danger")
            return False

        # Validar as datas de legalização
        if (
            request.form["last_legalization_date"]
            >= request.form["next_legalization_date"]
        ):
            flash(
                "A última data de legalização deve ser anterior à próxima data de legalização.",
                category="danger",
            )
            return False

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
        "edit_vehicle.html",
        vehicle=vehicle,
        VehicleType=VehicleType,
    )


def delete_vehicle(id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(id)

    # Remover o veículo do banco de dados
    db.session.delete(vehicle)
    db.session.commit()

    return redirect(url_for("admin_panel"))


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
        return redirect(
            url_for(
                "edit_vehicle",
                id=vehicle_id,
            )
        )


def client_login():
    if "user_id" in session:
        # Se o usuário já estiver logado, redirecione para a página de reserva
        # Verifica se há uma URL de redirecionamento armazenada
        redirect_url = session.pop("redirect_url", url_for("index"))
        return redirect(redirect_url)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        # Verifique as credenciais do cliente aqui (substitua com a sua lógica)
        client = Cliente.query.filter_by(email=email).first()
        if client.email == email and client.password == password:
            # Define a sessão para o usuário logado
            session["user_id"] = client.id

            # Verifica se há uma URL de redirecionamento armazenada
            redirect_url = session.pop("redirect_url", url_for("index"))
            return redirect(redirect_url)

        # Em caso de credenciais inválidas, exiba uma mensagem de erro
        error_message = "Credenciais de login inválidas. Por favor, tente novamente."
        return render_template("client_login.html", error_message=error_message)

    return render_template("client_login.html")


def client_logout():
    session.pop("user_id", None)  # Remove a chave 'client' da sessão
    # Redireciona para a página de login do cliente
    return redirect(url_for("client_login"))


def logout():
    # Remover a sessão de administrador
    session.pop("admin", None)
    return redirect(url_for("login"))


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

    return render_template(
        "maintenance_vehicle.html",
        vehicle=vehicle,
    )


def register_usage_route(vehicle_id):
    # Obter o veículo pelo ID
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # Registrar a utilização e verificar a próxima manutenção
    register_usage(vehicle)

    # Redirecionar de volta para a página de edição do veículo
    flash("Utilização registrada com sucesso!", "success")
    return redirect(
        url_for(
            "edit_vehicle",
            id=vehicle_id,
        )
    )
