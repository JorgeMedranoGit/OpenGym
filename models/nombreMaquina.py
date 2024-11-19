from database import db


class NombreMaquinas(db.Model):
    __tablename__ = 'nombremaquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("idnombremaquina", db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    codigomaquina = db.Column(db.String(50), nullable=False)  # Precio de venta, tipo decimal
    cantidad = db.Column(db.Integer, nullable=False)  # Stock disponible

    def __init__(self, nombre, codigomaquina, cantidad):
        self.nombre = nombre
        self.codigomaquina = codigomaquina
        self.cantidad = cantidad
    def __repr__(self):
        return f'<NombreMaquina {self.nombre}, Codigo: {self.codigomaquina}, Cantidad: {self.cantidad}>'
    