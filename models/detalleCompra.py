from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import db


class DetalleCompras(db.Model):
    __tablename__ = 'detallecompras'
    
    cantidad = db.Column(db.Integer, nullable=False)
    idcompra = db.Column(db.Integer, db.ForeignKey('compras.idcompra'), nullable=False)
    idproducto = db.Column(db.Integer, db.ForeignKey('productos.idp'), nullable=False)
    __table_args__ = (
        PrimaryKeyConstraint('idcompra', 'idproducto'),
    )
    compra = relationship("Compras", backref="detallecompras")
    producto = relationship("Productos", backref="detallecompras")
    
    def __init__(self, cantidad, idcompra, idproducto):
        self.cantidad = cantidad
        self.idcompra = idcompra
        self.idproducto = idproducto
    
    def __repr__(self):
        return f'<DetalleCompra: Compra {self.idcompra}, Producto {self.idproducto}, Cantidad: {self.cantidad}>'
