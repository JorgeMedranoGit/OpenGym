from sqlalchemy import Column, Integer, String, Numeric, Boolean
from sqlalchemy.orm import relationship
from database import db

class Membresias(db.Model):
    __tablename__ = 'membresia'

    idmembresia = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipomembresia = db.Column(db.String(30), nullable=False)
    costo = db.Column(db.Numeric(8,2), nullable=False)
    habilitado = db.Column(db.Boolean, default=True) 

    def __init__(self, tipomembresia, costo, habilitado=True):
        self.tipomembresia = tipomembresia
        self.costo = costo
        self.habilitado= habilitado

    def __repr__(self):
        return f'<Membresia(tipo="{self.tipomembresia}", costo={self.costo})>'

