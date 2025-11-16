from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30), nullable=False)

    # Una clienta puede tener muchas órdenes
    ordenes = db.relationship("Orden", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente {self.nombre}>"


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(120), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    imagen = db.Column(db.String(255))

    # Relación inversa: este producto puede aparecer en muchos items de orden
    orden_items = db.relationship("OrdenItem", back_populates="producto")

    def __repr__(self):
        return f"<Producto {self.marca} - {self.descripcion}>"


class Servicio(db.Model):
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    imagen = db.Column(db.String(255))

    # Este servicio puede aparecer en muchos items de orden
    orden_items = db.relationship("OrdenItem", back_populates="servicio")

    def __repr__(self):
        return f"<Servicio {self.descripcion}>"


class Orden(db.Model):
    __tablename__ = "ordenes"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relación con cliente (muchas órdenes -> un cliente)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    cliente = db.relationship("Cliente", back_populates="ordenes")

    # Relación con empleada (muchas órdenes -> una empleada)
    empleada_id = db.Column(db.Integer, db.ForeignKey("empleadas.id"), nullable=False)
    empleada = db.relationship("Empleada", back_populates="ordenes")

    # Items de esta orden (productos/servicios)
    items = db.relationship(
        "OrdenItem",
        back_populates="orden",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Orden {self.codigo}>"



class OrdenItem(db.Model):
    """
    Representa un renglón dentro de una orden.
    Puede ser un producto O un servicio.
    """
    __tablename__ = "orden_items"

    id = db.Column(db.Integer, primary_key=True)

    # Relación con la orden
    orden_id = db.Column(db.Integer, db.ForeignKey("ordenes.id"), nullable=False)
    orden = db.relationship("Orden", back_populates="items")

    # Indicamos si este item es producto o servicio
    tipo = db.Column(
        db.Enum("producto", "servicio", name="tipo_item"),
        nullable=False
    )

    # FK a producto o servicio (uno de los dos será NULL)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey("servicios.id"), nullable=True)

    producto = db.relationship("Producto", back_populates="orden_items")
    servicio = db.relationship("Servicio", back_populates="orden_items")

    # Campos adicionales del item
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    precio_unitario = db.Column(db.Float, nullable=False)  # snapshot del precio

    def __repr__(self):
        return f"<OrdenItem {self.tipo} x{self.cantidad}>"



class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str):
        """Genera y guarda el hash de la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide con el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Usuario {self.username} (admin={self.is_admin})>"
    
class Empleada(db.Model):
    __tablename__ = "empleadas"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Una empleada puede tener muchas órdenes
    ordenes = db.relationship("Orden", back_populates="empleada")

    def __repr__(self):
        return f"<Empleada {self.nombre}>"
