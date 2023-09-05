from app import app
from views import *
from admin_views import *

# Rotas para a aplicação Flask

# Página inicial
app.add_url_rule("/", view_func=index)

# Página de detalhes do veículo
app.add_url_rule("/vehicle/<int:id>", view_func=vehicle_details)

# Página de reserva do veículo
app.add_url_rule("/reserve/<int:id>", view_func=reserve, methods=["GET", "POST"])

# Processar pagamento
app.add_url_rule("/complete_payment", view_func=complete_payment, methods=["POST"])

# Página de confirmação de pagamento
app.add_url_rule("/order_confirmation", view_func=order_confirmation)

# Página de login do administrador
app.add_url_rule("/login", view_func=login, methods=["GET", "POST"])

# Painel de administração
app.add_url_rule("/admin", view_func=admin_panel, methods=["GET", "POST"])

# Listagem de veículos no painel de administração
app.add_url_rule("/admin/list-vehicles", view_func=list_vehicles)

# Visualizar detalhes do veículo pelo admin
app.add_url_rule("/admin/view_vehicle/<int:id>", view_func=view_vehicle)

# Página de adição de veículos
app.add_url_rule("/add_vehicle", view_func=add_vehicle, methods=["GET", "POST"])

# Página de edição de veículos
app.add_url_rule(
    "/edit_vehicle/<int:id>", view_func=edit_vehicle, methods=["GET", "POST"]
)

# Página de exclusão de veículos
app.add_url_rule("/delete_vehicle/<int:id>", view_func=delete_vehicle, methods=["POST"])

# Página de exclusão de imagem
app.add_url_rule(
    "/delete_image/<path:image_path>/<int:vehicle_id>",
    view_func=delete_image,
    methods=["GET", "POST"],
)

# Página de login do cliente
app.add_url_rule("/client_login", view_func=client_login, methods=["GET", "POST"])

# Logout do cliente
app.add_url_rule("/client_logout", view_func=client_logout)

# Logout do admin
app.add_url_rule("/logout", view_func=logout)

# Página de registro do cliente
app.add_url_rule("/register_client", view_func=register_client, methods=["GET", "POST"])

# Página de confirmação de legalização do veículo
app.add_url_rule(
    "/legalize_vehicle/<int:id>", view_func=legalize_vehicle, methods=["POST"]
)

# Página de manutenção do veículo
app.add_url_rule(
    "/admin/maintenance_vehicle/<int:id>",
    view_func=maintenance_vehicle,
    methods=["GET", "POST"],
)

# Rota para atualizar o número de utilizações do veículo
app.add_url_rule(
    "/register_usage/<int:vehicle_id>", view_func=register_usage_route, methods=["POST"]
)

# Página de visualização das reservas do cliente
app.add_url_rule("/client_reservations", view_func=client_reservations)

# Página para cancelar reserva do cliente
app.add_url_rule(
    "/cancel_reservation/<int:id>", view_func=cancel_reservation, methods=["POST"]
)

# Página de edição do cadastro do cliente
app.add_url_rule("/edit_client", view_func=edit_client, methods=["GET"])

# Página para atualizar o cadastro do cliente no banco de dados
app.add_url_rule("/update_client", view_func=update_client, methods=["POST"])

# Página de visualização de categorias
app.add_url_rule("/admin/categorias", view_func=categorias, methods=["GET", "POST"])

# Página de edição de categorias
app.add_url_rule(
    "/admin/categorias/edit/<int:id>",
    view_func=editar_categoria,
    methods=["GET", "POST"],
)

# Página de remoção de categorias
app.add_url_rule(
    "/admin/categorias/delete/<int:id>",
    view_func=deletar_categoria,
    methods=["GET", "POST"],
)

# Página de listagem de clientes
app.add_url_rule("/list_clients", view_func=list_clients)

# Página para excluir um cliente
app.add_url_rule("/delete_client/<int:id>", view_func=delete_client, methods=["POST"])

# Página para editar um cliente existente pelo admin
app.add_url_rule(
    "/admin_edit_client/<int:id>", view_func=admin_edit_client, methods=["GET", "POST"]
)

# Página para exportar listagem de veículos para CSV
app.add_url_rule("/export_csv", view_func=export_csv, methods=["GET"])

# Página para exportar listagem de veículos para Excel
app.add_url_rule("/export_excel", view_func=export_excel, methods=["GET"])
