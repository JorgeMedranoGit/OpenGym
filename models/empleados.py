from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from database import db

# Importar db desde app.py



Base = declarative_base()


class Empleado(db.Model):
    __tablename__ = 'empleados'

    idempleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=True)
    carnet = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    sueldo = db.Column(db.Numeric(10, 2), nullable=True)

    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'