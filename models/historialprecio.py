from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database import db

Base = declarative_base()


class HistorialPrecios(db.Model):
    __tablename__ = 'historialprecios'  # Nombre de la tabla en la base de datos

    idprecio = db.Column("idprecio", db.Integer, primary_key=True, autoincrement=True) 
    precioventa = db.Column(db.Numeric(10, 2), nullable=False)  # Precio de venta, tipo decimal
    fecha = db.Column(db.DateTime(50), nullable=False)
    idp = db.Column(db.Integer, db.ForeignKey('productos.idp'), nullable=False)

    def __init__(self, precioventa, fecha, idp):
        self.precioventa = precioventa
        self.fecha = fecha
        self.idp = idp
    def __repr__(self):
        return f'<Producto {self.precioventa}, Precio: {self.fecha}, Stock: {self.idp}>'