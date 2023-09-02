from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime, date, timedelta

db = SQLAlchemy()


# Definir as opções válidas para o campo 'type' (Carro e Mota)
class VehicleType(Enum):
    CARRO = "Carro"
    MOTA = "Mota"


# Classe para o modelo de Veículo
class Veiculo(db.Model):
    __tablename__ = "veiculos"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(VehicleType), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    status = db.Column(db.Boolean, default=True)
    #categoria = db.Column(db.String(50), nullable=False, default="")
    in_maintenance = db.Column(db.Boolean, default=False)
    last_maintenance_date = db.Column(db.Date)
    next_maintenance_date = db.Column(db.Date)
    maintenance_history = db.Column(db.String(1000), default="")
    last_legalization_date = db.Column(db.Date)
    next_legalization_date = db.Column(db.Date)
    legalization_history = db.Column(db.String(1000), default="")
    imagens = db.Column(db.String(1000))
    available_from = db.Column(db.Date, nullable=True)
    num_uses = db.Column(db.Integer, default=0)
    max_uses_before_maintenance = db.Column(db.Integer, default=50)
    categoria = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    reservations = db.relationship(
        "Reservation",
        backref="veiculos",
        lazy=True,
    )

    def __init__(self, type, brand, model, year, price_per_day, categoria=""):
        self.type = type
        self.brand = brand
        self.model = model
        self.year = year
        self.price_per_day = price_per_day
        self.categoria = categoria
        self.maintenance_history = ""
        self.last_legalization_date = None
        self.next_legalization_date = None
        self.legalization_history = ""
        self.imagens = ""

    def update_categoria(self):
        if self.price_per_day <= 50:
            self.categoria = "Económico"
        elif self.price_per_day <= 250:
            self.categoria = "Silver"
        else:
            self.categoria = "Gold"

    def initialize_vehicle(self):
        # Define a data de criação do veículo como a data de última legalização
        self.last_legalization_date = date.today()

        # Calcular a data da próxima legalização (1 ano à frente)
        one_year_later = date.today() + timedelta(days=365)
        self.next_legalization_date = one_year_later

        # Atualizar a categoria do veículo com base no preço por dia
        if self.price_per_day >= 250:
            self.categoria = "Gold"
        elif self.price_per_day >= 50:
            self.categoria = "Silver"
        else:
            self.categoria = "Económico"

        # Definir as datas de manutenção
        self.last_maintenance_date = datetime.now().date()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)
        # Define a disponibilidade como hoje por padrão
        self.available_from = date.today()

    def start_maintenance(self):
        self.in_maintenance = True
        self.status = False
        self.last_maintenance_date = date.today()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=30)

    def end_maintenance(self):
        self.in_maintenance = False
        self.status = True
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)


# Modelo de classe para clientes
class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    apelido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    morada = db.Column(db.String(200), nullable=False)
    nif = db.Column(db.Integer, unique=True, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False, default=50)
    password = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(20), nullable=False, default="Económico")
    reservations = db.relationship(
        "Reservation",
        backref="clientes",
        lazy=True,
    )

    def __init__(
        self,
        nome,
        apelido,
        email,
        telefone,
        data_nascimento,
        morada,
        nif,
        password,
        categoria,
    ):
        self.nome = nome
        self.apelido = apelido
        self.email = email
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.morada = morada
        self.nif = nif
        self.password = password
        self.categoria = categoria

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

    def __repr__(self):
        return f"<Cliente {self.nome} {self.apelido}>"


# Classe para o modelo de Reserva
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
        name="fk_reservation_customer",
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("veiculos.id"),
        nullable=False,
        name="fk_reservation_vehicle",
    )
    status = db.Column(db.String(20), nullable=False, default="Ativa")
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def add_reservations(self):
        db.session.add(self)
        db.session.commit()

    def update_completed_reservations():
        today = date.today()
        completed_reservations = Reservation.query.filter(
            Reservation.end_date < today, Reservation.status != "Concluída"
        ).all()

        for reservation in completed_reservations:
            reservation.status = "Concluída"
            db.session.commit()


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
    )

    # Relacionamento entre Categoria e Veículos
    veiculos = db.relationship(
        "Veiculo",
        lazy=True,
    )

    def __init__(self, nome):
        self.nome = nome
