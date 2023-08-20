from flask import Flask
from controllers import (
    index,
    vehicle_details,
    reserve,
    complete_payment,
    order_confirmation,
    admin_panel,
    view_vehicle,
    add_vehicle,
    edit_vehicle,
    delete_vehicle,
    delete_image,
    client_login,
    client_logout,
    logout,
    register_client,
    legalize_vehicle,
    maintenance_vehicle,
    register_usage_route,
)

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

# Rota para exclusão de imagem
app.route("/delete_image/<path:image_path>/<int:vehicle_id>", methods=["POST"])(
    delete_image
)

# Rota para a página de login do cliente
app.route("/client_login", methods=["GET", "POST"])(client_login)

# Rota para logout do cliente
app.route("/client_logout")(client_logout)

# Rota para logout do admin
app.route("/logout")(logout)

# Rota para a página de registro do cliente
app.route("/register_client", methods=["GET", "POST"])(register_client)

# Rota para confirmar a legalização do veículo
app.route("/legalize_vehicle/<int:id>", methods=["POST"])(legalize_vehicle)

# Rota para manutenção do veículo
app.route("/admin/maintenance_vehicle/<int:id>", methods=["GET", "POST"])(
    maintenance_vehicle
)
# Rota para atualizar o número de utilização do veículo
app.route("/register_usage/<int:vehicle_id>", methods=["POST"])(register_usage_route)
