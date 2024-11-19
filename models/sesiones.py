from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class Sesion(db.Model):
    __tablename__= 'sesion'

    idsesion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fechasesion = db.Column(db.Date, default=db.func.current_date())
    costo = db.Column(db.Numeric(8,2), nullable=True)
    horaentrada= db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    tipo_sesion = db.Column(db.String(10), nullable=False)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.idcliente', ondelete='CASCADE'), nullable=True)
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado', ondelete='SET NULL'), nullable=True)
    idpago= db.Column(db.Integer, db.ForeignKey('pago.idpago', ondelete='CASCADE'), nullable=True)
    

    def __init__(self, tipo_sesion, idcliente=None, costo=None, idempleado=None, idpago=None):
        self.tipo_sesion = tipo_sesion
        self.idcliente = idcliente
        self.costo = costo
        self.idempleado = idempleado
        self.idpago = idpago

    def __repr__(self):
        return (f'<Sesion(idsesion={self.idsesion}, fechasesion={self.fechasesion}, '
                f'costo={self.costo}, tipo_sesion={self.tipo_sesion}, idcliente={self.idcliente}, idempleado={self.idempleado} , idpago={self.idpago})>')