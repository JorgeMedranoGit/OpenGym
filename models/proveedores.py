from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from database import db


Base = declarative_base()


class Proveedores(db.Model):
    __tablename__ = 'proveedores'  # Nombre de la tabla en la base de datos

    _id = db.Column("idproveedor", db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(30), nullable=False)
    telefono = db.Column(db.String(9), nullable=False)
    correo = db.Column(db.String(50), nullable=False)
    habilitado = db.Column(db.Boolean, nullable=False)

    def __init__(self, nombre, telefono, correo, habilitado):
        self.nombre = nombre
        self.telefono = telefono
        self.correo = correo
        self.habilitado = habilitado

    def __repr__(self):
        return f'<Proveedor {self.nombre}, Telefono: {self.telefono}, Correo: {self.correo}>'
