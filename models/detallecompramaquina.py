from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from database import db

Base = declarative_base()

class DetalleCompraMaquina(db.Model):
    __tablename__ = 'detallecompramaquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("id", db.Integer, primary_key=True, autoincrement=True)  # ID del detalle de la compra
    idcompra = db.Column(db.Integer, db.ForeignKey('compramaquina.idcompra'), nullable=False)  # ID de la compra
    idnommaquina = db.Column(db.Integer, db.ForeignKey('nombremaquina.idnombremaquina'), nullable=False)  # ID de la máquina
    cantidad = db.Column(db.Integer, nullable=False)  # Cantidad comprada
    proveedor = db.Column(db.Integer, db.ForeignKey('proveedores.idproveedor'), nullable=False)  # ID del proveedor
    preciounitario = db.Column(db.Float, nullable=False)
    # Relaciones
    compra = db.relationship('CompraMaquina', backref='detalles')  # Relación con CompraMaquina
    nombremaquina = db.relationship('NombreMaquinas', backref='detalles')  # Relación con NombreMaquina
    proveedor_rel = db.relationship('Proveedores', backref='detalles')  # Relación con Proveedor

    def __init__(self, idcompra, idnommaquina, cantidad, proveedor, preciounitario):
        self.idcompra = idcompra
        self.idnommaquina = idnommaquina
        self.cantidad = cantidad
        self.proveedor = proveedor
        self.preciounitario = preciounitario

    def __repr__(self):
        return f'<DetalleCompraMaquina {self._id}, IdCompra: {self.idcompra}, IdMaquina: {self.idmaquina}, Cantidad: {self.cantidad}, Proveedor: {self.proveedor}>'