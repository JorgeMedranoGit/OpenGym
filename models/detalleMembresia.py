from sqlalchemy import Column, Integer, Date, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class DetalleMembresia(db.Model):
    __tablename__ = 'detallemembresia'

    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.idcliente', ondelete='CASCADE'), primary_key=True, nullable=False)
    idmembresia = db.Column(db.Integer, db.ForeignKey('membresia.idmembresia', ondelete='CASCADE'), primary_key=True, nullable=False)
    fechainicio = db.Column(db.Date, nullable=False)
    fechavencimiento = db.Column(db.Date, nullable=False)
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado', ondelete='SET NULL'))

    __table_args__ = (
        PrimaryKeyConstraint('idcliente', 'idmembresia'),
    )

    cliente = relationship("Clientes", backref="detallemembresia")
    membresia = relationship("Membresias", backref="detallemembresia")

    def __init__(self, idcliente, idmembresia, fechainicio, fechavencimiento, idempleado=None):
        self.idcliente = idcliente
        self.idmembresia = idmembresia
        self.fechainicio = fechainicio
        self.fechavencimiento = fechavencimiento
        self.idempleado = idempleado
    
    def __repr__(self):
        return f'<DetalleMembresia(idcliente={self.idcliente}, idmembresia={self.idmembresia}, fechainicio={self.fechainicio}, fechavencimiento={self.fechavencimiento})>'
