from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class TurnoCliente(db.Model):
    __tablename__ = 'turnocliente'

    idturnocliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idcliente = db.Column(db.Integer, db.ForeignKey('clientes.idcliente', ondelete='CASCADE'), nullable=False)
    descripcion = db.Column(db.String(50), nullable=True)
    comienzo = db.Column(db.DateTime, nullable=False)
    fin = db.Column(db.DateTime, nullable=False)

    cliente = relationship('Clientes', backref='turnos')

    def __init__(self, idcliente, comienzo, fin, descripcion=None):
        self.idcliente = idcliente
        self.descripcion = descripcion
        self.comienzo = comienzo
        self.fin = fin

    def __repr__(self):
        return (f'<TurnoCliente(idturnocliente={self.idturnocliente}, idcliente={self.idcliente}, '
                f'descripcion={self.descripcion}, comienzo={self.comienzo}, fin={self.fin})>')