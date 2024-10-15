from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from database import db

Base = declarative_base()


class Productos(db.Model):
    __tablename__ = 'productos'  # Nombre de la tabla en la base de datos

    _id = db.Column("idp", db.Integer, primary_key=True, autoincrement=True)  # Columna de identificación
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del producto
    preciov = db.Column(db.Numeric(10, 2), nullable=False)  # Precio de venta, tipo decimal
    stock = db.Column(db.Integer, nullable=False)  # Stock disponible

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.preciov = precio
        self.stock = stock
    def __repr__(self):
        return f'<Producto {self.nombre}, Precio: {self.previov}, Stock: {self.stock}>'