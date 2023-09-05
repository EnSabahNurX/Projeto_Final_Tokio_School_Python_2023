from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime, date, timedelta

db = SQLAlchemy()


class VehicleType(Enum):
    """
    Enumeração que define os tipos de veículos (Carro e Mota).
    """

    CARRO = "Carro"
    MOTA = "Mota"


class Categoria(db.Model):
    """
    Modelo de Categoria de Veículo.
    """

    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, nome):
        self.nome = nome


class Veiculo(db.Model):
    """
    Modelo de Veículo.
    """

    __tablename__ = "veiculos"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(VehicleType), nullable=False)
    brand = db.Column(db.String(100), nullable=False, index=True)
    model = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    status = db.Column(db.Boolean, default=True)
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
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=False)
    categoria = db.relationship("Categoria", backref=db.backref("veiculos", lazy=True))
    reservations = db.relationship(
        "Reservation",
        backref="veiculos",
        lazy=True,
    )

    def __init__(self, type, brand, model, year, price_per_day, categoria=None):
        """
        Inicializa um veículo com os parâmetros especificados.
        """
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

    def initialize_vehicle(self):
        """
        Inicializa as datas e valores padrão para um veículo novo.
        """
        self.last_legalization_date = date.today()
        one_year_later = date.today() + timedelta(days=365)
        self.next_legalization_date = one_year_later
        self.last_maintenance_date = datetime.now().date()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)
        self.available_from = date.today()

    def start_maintenance(self):
        """
        Inicia o registro de manutenção para um veículo.
        """
        self.in_maintenance = True
        self.status = False
        self.last_maintenance_date = date.today()
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=30)

    def end_maintenance(self):
        """
        Finaliza o registro de manutenção para um veículo.
        """
        self.in_maintenance = False
        self.status = True
        self.next_maintenance_date = self.last_maintenance_date + timedelta(days=180)


class Cliente(db.Model):
    """
    Modelo de Cliente.
    """

    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    apelido = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20), nullable=False, index=True)
    data_nascimento = db.Column(db.Date, nullable=False)
    morada = db.Column(db.String(200), nullable=False)
    nif = db.Column(db.Integer, unique=True, nullable=False, index=True)
    price_per_day = db.Column(db.Float, nullable=False, default=50)
    password = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(20), nullable=False, default="Económico")
    reservations = db.relationship(
        "Reservation",
        backref="cliente",
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
        """
        Inicializa um cliente com os parâmetros especificados.
        """
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
        """
        Verifica se o cliente está ativo.
        """
        return True

    def is_authenticated(self):
        """
        Verifica se o cliente está autenticado.
        """
        return True

    def get_id(self):
        """
        Obtém o ID do cliente.
        """
        return self.id

    def __repr__(self):
        """
        Representação de string do objeto Cliente.
        """
        return f"<Cliente {self.nome} {self.apelido}>"


# Classe para o modelo de Reserva
class Reservation(db.Model):
    """
    Modelo de Reserva.
    """

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("clientes.id"),
        nullable=False,
        name="fk_reservation_customer",
        index=True,
    )
    vehicle_id = db.Column(
        db.Integer,
        db.ForeignKey("veiculos.id"),
        nullable=False,
        name="fk_reservation_vehicle",
        index=True,
    )
    status = db.Column(db.String(20), nullable=False, default="Ativa")
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def add_reservations(self):
        """
        Adiciona uma reserva ao banco de dados.
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def update_completed_reservations():
        """
        Atualiza as reservas concluídas para o status "Concluída".
        """
        today = date.today()
        completed_reservations = Reservation.query.filter(
            Reservation.end_date < today, Reservation.status != "Concluída"
        ).all()

        for reservation in completed_reservations:
            reservation.status = "Concluída"
            db.session.commit()
