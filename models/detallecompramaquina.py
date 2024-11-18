from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from database import db

Base = declarative_base()

class DetalleCompraMaquina(db.Model):
    __tablename__ = 'detallecompramaquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)  # ID del detalle de la compra
    idcompra = db.Column(db.Integer, db.ForeignKey('compramaquina.idcompra'), nullable=False)  # ID de la compra
    cantidad = db.Column(db.Integer, nullable=False)  # Cantidad comprada
    preciounitario = db.Column(db.Float, nullable=False)

    def __init__(self, idcompra, cantidad, preciounitario):
        self.idcompra = idcompra
        self.cantidad = cantidad
        self.preciounitario = preciounitario

    def __repr__(self):
        return f'<DetalleCompraMaquina {self._id}, IdCompra: {self.idcompra}, IdMaquina: {self.idmaquina}, Cantidad: {self.cantidad}, Proveedor: {self.proveedor}>'