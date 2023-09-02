from app import app
from views import *
from admin_views import *

# Rota inicial
app.add_url_rule(
    "/",
    view_func=index,
)

# Rota para a página de detalhes do veículo
app.add_url_rule(
    "/vehicle/<int:id>",
    view_func=vehicle_details,
)

# Rota para a página de reserva do veículo
app.add_url_rule(
    "/reserve/<int:id>",
    view_func=reserve,
    methods=["GET", "POST"],
)

# Rota para processar o pagamento
app.add_url_rule(
    "/complete_payment",
    view_func=complete_payment,
    methods=["POST"],
)

# Rota para a página de confirmação de pagamento
app.add_url_rule(
    "/order_confirmation",
    view_func=order_confirmation,
)


# Rota para a página de login do administrador
app.add_url_rule(
    "/login",
    view_func=login,
    methods=["GET", "POST"],
)

# Rota para o painel de administração
app.add_url_rule(
    "/admin",
    view_func=admin_panel,
    methods=["GET", "POST"],
)

# Rota para visualisar os detalhes do veículo pelo admin
app.add_url_rule(
    "/admin/view_vehicle/<int:id>",
    view_func=view_vehicle,
)

# Rota para a página de adicionar veículos
app.add_url_rule(
    "/add_vehicle",
    view_func=add_vehicle,
    methods=["GET", "POST"],
)

# Rota para a página de edição de veículo
app.add_url_rule(
    "/edit_vehicle/<int:id>",
    view_func=edit_vehicle,
    methods=["GET", "POST"],
)

# Rota para exclusão de veículo
app.add_url_rule(
    "/delete_vehicle/<int:id>",
    view_func=delete_vehicle,
    methods=["POST"],
)

# Rota para exclusão de imagem
app.add_url_rule(
    "/delete_image/<path:image_path>/<int:vehicle_id>",
    view_func=delete_image,
    methods=["GET", "POST"],
)

# Rota para a página de login do cliente
app.add_url_rule(
    "/client_login",
    view_func=client_login,
    methods=["GET", "POST"],
)

# Rota para logout do cliente
app.add_url_rule(
    "/client_logout",
    view_func=client_logout,
)

# Rota para logout do admin
app.add_url_rule(
    "/logout",
    view_func=logout,
)

# Rota para a página de registro do cliente
app.add_url_rule(
    "/register_client",
    view_func=register_client,
    methods=["GET", "POST"],
)

# Rota para confirmar a legalização do veículo
app.add_url_rule(
    "/legalize_vehicle/<int:id>",
    view_func=legalize_vehicle,
    methods=["POST"],
)

# Rota para manutenção do veículo
app.add_url_rule(
    "/admin/maintenance_vehicle/<int:id>",
    view_func=maintenance_vehicle,
    methods=["GET", "POST"],
)
# Rota para atualizar o número de utilização do veículo
app.add_url_rule(
    "/register_usage/<int:vehicle_id>",
    view_func=register_usage_route,
    methods=["POST"],
)

# Rota para visualizar as reservas do cliente
app.add_url_rule(
    "/client_reservations",
    view_func=client_reservations,
)

# Rota para cancelar reserva do cliente
app.add_url_rule(
    "/cancel_reservation/<int:id>",
    view_func=cancel_reservation,
    methods=["POST"],
)

# Rota para editar cadastro do cliente
app.add_url_rule(
    "/edit_client",
    view_func=edit_client,
    methods=["GET"],
)

# Rota para atualizar no banco de dados o cadastro do cliente
app.add_url_rule(
    "/update_client",
    view_func=update_client,
    methods=["POST"],
)

# Rota para visualizar categorias
app.add_url_rule(
    "/admin/categorias",
    view_func=categorias,
    methods=["GET", "POST"],
)

# Rota para editar categorias
app.add_url_rule(
    "/admin/categorias/edit/<int:id>",
    view_func=editar_categoria,
    methods=["GET", "POST"],
)

# Rota para remover categorias
app.add_url_rule(
    "/admin/categorias/delete/<int:id>",
    view_func=deletar_categoria,
    methods=["GET", "POST"],
)
