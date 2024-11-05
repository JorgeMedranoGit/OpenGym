from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import relationship
from datetime import datetime
from database import db

Base = declarative_base()


class Entregas(db.Model):
    __tablename__ = 'entregas'
 
    identrega = db.Column("identrega", db.Integer, primary_key=True, autoincrement=True)
    fechapedido = db.Column(db.DateTime(50), nullable=False)
    metodopago = db.Column(db.String(50), nullable=False)
    idproveedor = db.Column(db.Integer, db.ForeignKey('proveedores.idproveedor'), nullable=False)
 
    proveedor = relationship("Proveedores", backref="entregas")

    def __init__(self, fechapedido, metodopago, idproveedor):
        self.fechapedido = fechapedido
        self.metodopago = metodopago
        self.idproveedor = idproveedor
    def __repr__(self):
        return f'<Fecha: {self.fechapedido} Pago: {self.metodopago}'