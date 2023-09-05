from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from models import db
from config import Config

# Craição do app para rodar o server Flask
app = Flask(__name__)

# Carrega as configurações relacionadas ao Flask de config.py
app.config.from_object(Config)

# Inicialização do banco de dados
db.init_app(app)

# Cria função para execução de migrações para as alterações no esquema da base de dados, por exemplo:
# flask db init
# flask db migrate && flask db upgrade
migrate = Migrate(app, db)

# Registrar as rotas do arquivo urls.py, é feito a importação somente após criado o app e feita a inicialização do banco de dados
from urls import *


# Função de middleware para verificar a sessão de administrador
@app.before_request
def check_admin_session():
    """
    Middleware para verificar se o usuário está autenticado como administrador
    antes de acessar rotas protegidas.
    """
    # Lista de rotas que requerem autenticação de administrador
    admin_routes = ["/admin", "/add_vehicle", "/edit_vehicle/", "/delete_vehicle/"]

    if request.path in admin_routes:
        if "admin" not in session:
            return redirect(url_for("login"))


# Função para verificar o status de manutenção do veículo
def check_maintenance_status():
    """
    Verifica o status de manutenção de veículos e atualiza conforme necessário.
    """
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


# Criar um scheduler para executar tarefas em segundo plano
scheduler = BackgroundScheduler()
scheduler.start()

# Agendar a função para ser executada diariamente à meia-noite (00:00)
scheduler.add_job(
    check_maintenance_status, "interval", days=1, start_date="2023-07-27 00:00:00"
)

# Ao sair da aplicação, finalizar o scheduler
atexit.register(lambda: scheduler.shutdown())


# Criação das tabelas do banco de dados, este comando verifica automaticamente se já existe a tabela
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == "__main__":
    app.run(debug=True)
