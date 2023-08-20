from flask import Flask
from controllers import *

app = Flask(__name__)

# Rotas

# Rota inicial
app.route("/")(index)

# Rota para a página de detalhes do veículo
app.route("/vehicle/<int:id>")(vehicle_details)

# Rota para a página de reserva do veículo
app.route("/reserve/<int:id>", methods=["GET", "POST"])(reserve)

# Rota para processar o pagamento
app.route("/complete_payment", methods=["POST"])(complete_payment)

# Rota para a página de confirmação de pagamento
app.route("/order_confirmation")(order_confirmation)

# Função de middleware para verificar a sessão de administrador
app.before_request(check_admin_session)

# Rota para a página de login do administrador
app.route("/login", methods=["GET", "POST"])(login)

# Rota para o painel de administração
app.route("/admin", methods=["GET", "POST"])(admin_panel)

# Rota para visualisar os detalhes do veículo pelo admin
app.route("/admin/view_vehicle/<int:id>")(view_vehicle)

# Rota para a página de adicionar veículos
app.route("/add_vehicle", methods=["GET", "POST"])(add_vehicle)

# Rota para a página de edição de veículo
app.route("/edit_vehicle/<int:id>", methods=["GET", "POST"])(edit_vehicle)

# Rota para exclusão de veículo
app.route("/delete_vehicle/<int:id>", methods=["POST"])(delete_vehicle)