import os
import pytz

# Caminho do banco de dados
db_folder = os.path.join(os.path.dirname(__file__), "database")
db_path = os.path.join(db_folder, "database.db")

# Verificar e criar o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Se a pasta 'static/images' não existir, crie-a
if not os.path.exists("static/images"):
    os.makedirs("static/images")


class Config:
    SECRET_KEY = "sua_chave_secreta_aqui"
    TIMEZONE = pytz.timezone("Europe/Lisbon")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static/images")
    BOOTSTRAP_BOOTSWATCH_THEME = "cyborg"
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_FONTAWESOME = True
    BOOTSTRAP_COLORS = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#00bcd4",
    }

    BOOTSTRAP_FONTAWESOME_ICONS = [
        "fas fa-car",
        "fas fa-motorcycle",
    ]
