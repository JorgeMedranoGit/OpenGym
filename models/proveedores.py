from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from database import db


Base = declarative_base()



class Proveedores(db.Model):
    __tablename__ = 'proveedores'  # Nombre de la tabla en la base de datos

    _id = db.Column("idproveedor", db.Integer, primary_key=True, autoincrement=True)  # Columna de identificación
    nombre = db.Column(db.String(30), nullable=False)  # Nombre del producto
    telefono = db.Column(db.String(9), nullable=False)  # Precio de venta, tipo decimal
    correo = db.Column(db.String(50), nullable=False)  # Stock disponible

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.telefono = precio
        self.correo = stock
    def __repr__(self):
        return f'<Proveedor {self.nombre}, Telefono: {self.telefono}, Correo: {self.correo}>'
    