from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from database import db

Base = declarative_base()
# Comentaio Nafta

class Clientes(db.Model):
    __tablename__ = 'clientes'
 
    _id = db.Column("idcliente", db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    carnet = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    tipocliente = db.Column(db.String(50), nullable=False)
    activo = db.Column(db.Boolean, nullable=False, default=True)
 
    def __init__(self, nombre, apellido, carnet, telefono, tipocliente, activo=True):
        self.nombre = nombre
        self.apellido = apellido
        self.carnet = carnet
        self.telefono = telefono
        self.tipocliente = tipocliente
        self.activo = activo
 
    def __repr__(self):
        return f'<Cliente {self.nombre} {self.apellido}, Tipo: {self.tipocliente}, Activo: {self.activo}>'