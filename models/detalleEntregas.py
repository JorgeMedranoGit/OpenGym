from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import db


class DetalleEntregas(db.Model):
    __tablename__ = 'detalleentregas'
    
    cantidad = db.Column(db.Integer, nullable=False)
    preciocompra = db.Column(db.Numeric(10, 2), nullable=False)
    identrega = db.Column(db.Integer, db.ForeignKey('entregas.identrega'), nullable=False)
    idp = db.Column(db.Integer, db.ForeignKey('productos.idp'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('identrega', 'idp'),
    )
    compra = relationship("Entregas", backref="detalleentregas")
    producto = relationship("Productos", backref="detalleentregas")
    
    def __init__(self, cantidad, preciocompra,identrega, idproducto):
        self.cantidad = cantidad
        self.preciocompra = preciocompra
        self.identrega = identrega
        self.idp = idproducto
    
