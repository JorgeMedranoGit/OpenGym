from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class Sesion(db.Model):
    __tablename__= 'sesion'

    idsesion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechasesion = db.Column(db.Date, default=db.func.current_date())
    costo = db.Column(db.Numeric(8,2), nullable=False)

    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.idcliente', ondelete='CASCADE'), nullable=False)
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado', ondelete='SET NULL'), nullable=True)
    

    def __init__(self, idcliente, costo, fechasesion=None, idempleado=None):
        self.idcliente = idcliente
        self.costo = costo
        self.fechasesion = fechasesion if fechasesion else db.func.current_date()
        self.idempleado = idempleado

    def __repr__(self):
        return (f'<Sesion(idsesion={self.idsesion}, fechasesion={self.fechasesion}, '
                f'costo={self.costo}, idcliente={self.idcliente}, idempleado={self.idempleado})>')