from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from database import db
from datetime import datetime  # Importar datetime para establecer la fecha actual

Base = declarative_base()

class CompraMaquina(db.Model):
    __tablename__ = 'compramaquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("idcompra", db.Integer, primary_key=True, autoincrement=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Almacena la fecha y hora de la compra
    idempleado = db.Column(db.String(50), nullable=False)

    def __init__(self, idempleado):
        self.idempleado = idempleado

    def __repr__(self):
        return f'<CompraMaquina {self._id}, Fecha: {self.fecha}, IdEmpleado: {self.idempleado}>'