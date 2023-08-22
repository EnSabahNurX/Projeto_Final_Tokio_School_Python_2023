import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from datetime import datetime, date, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from werkzeug.utils import secure_filename
from decorators import login_required
from models import db
from models import db, Vehicle, VehicleType, Cliente
from config import Config
from views import *


app = Flask(__name__)
app.config.from_object(Config)


# Inicialização do banco de dados
db.init_app(app)
migrate = Migrate(app, db)

# Registrar as rotas do arquivo urls.py
from urls import *


# Função de middleware para verificar a sessão de administrador
@app.before_request
def check_admin_session():
    # Lista de rotas que requerem autenticação de administrador
    admin_routes = ["/admin", "/add_vehicle", "/edit_vehicle/", "/delete_vehicle/"]

    if request.path in admin_routes:
        if "admin" not in session:
            return redirect(url_for("login"))


# Criar um scheduler para executar tarefas em segundo plano
scheduler = BackgroundScheduler()
scheduler.start()

# Agendar a função para ser executada diariamente à meia-noite (00:00)
scheduler.add_job(
    check_maintenance_status, "interval", days=1, start_date="2023-07-27 00:00:00"
)

# Ao sair da aplicação, finalizar o scheduler
atexit.register(lambda: scheduler.shutdown())


# Criação das tabelas do banco de dados
with app.app_context():
    db.create_all()

# Executar a aplicação Flask com debug mode habilitado
if __name__ == "__main__":
    app.run(debug=True)
