from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import db


class EntregaEstado(db.Model):
    __tablename__ = 'entregaestado'
    
    fechaestado = db.Column(db.DateTime(50), nullable=False)
    identrega = db.Column(db.Integer, db.ForeignKey('entregas.identrega'), nullable=False)
    idestado = db.Column(db.Integer, db.ForeignKey('estados.idestado'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('identrega', 'idestado'),
    )
    compra = relationship("Entregas", backref="entregaestado")
    producto = relationship("Estados", backref="entregaestado")
    
    def __init__(self, fechaestado, identrega, idestado):
        self.fechaestado = fechaestado
        self.identrega = identrega
        self.idestado = idestado
    
