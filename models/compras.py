from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relationship
from datetime import datetime
from database import db

Base = declarative_base()


class Compras(db.Model):
    __tablename__ = 'compras'
 
    idcompra = db.Column("idcompra", db.Integer, primary_key=True, autoincrement=True)
    fechacompra = db.Column(db.DateTime(50), nullable=False)
    metodopago = db.Column(db.String(50), nullable=False)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.idcliente'), nullable=False)
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado'), nullable=False)
 
    cliente = relationship("Clientes", backref="compras")
    empleado = relationship("Empleado", backref="compras")

    def __init__(self, fechacompra, metodopago, idcliente, idempleado):
        self.fechacompra = fechacompra
        self.metodopago = metodopago
        self.idcliente = idcliente
        self.idempleado = idempleado
    def __repr__(self):
        return f'<Fecha: {self.fechacompra} Pago: {self.metodopago}'