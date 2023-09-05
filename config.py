import os
import pytz

# Caminhos do banco de dados e imagens estáticas
db_folder = os.path.join(os.path.dirname(__file__), "database")
db_path = os.path.join(db_folder, "database.db")

# Verifica e cria o diretório "database" se não existir
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# Cria o diretório "static/images" se não existir
static_images_folder = os.path.join(os.path.dirname(__file__), "static/images")
if not os.path.exists(static_images_folder):
    os.makedirs(static_images_folder)


class Config:
    """
    Configurações da aplicação Flask.
    """

    SECRET_KEY = "sua_chave_secreta_aqui"
    TIMEZONE = pytz.timezone("Europe/Lisbon")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = static_images_folder

    # Configurações do Bootstrap
    BOOTSTRAP_BOOTSWATCH_THEME = "yeti"
    BOOTSTRAP_USE_MINIFIED = True
    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_FONTAWESOME = True

    # Cores personalizadas do Bootstrap
    BOOTSTRAP_COLORS = {
        "primary": "#007bff",
        "secondary": "#6c757d",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#ffc107",
        "info": "#00bcd4",
    }

    # Ícones do Font Awesome usados no Bootstrap
    BOOTSTRAP_FONTAWESOME_ICONS = [
        "fas fa-car",
        "fas fa-motorcycle",
    ]
