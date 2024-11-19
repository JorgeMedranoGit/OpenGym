from sqlalchemy import Column, Integer, String, Float, ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from database import db

class Pago(db.Model):
    __tablename__ = 'pago'

    idpago = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idcliente = db.Column(db.Integer, nullable=False)
    idmembresia = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Numeric(8,2), nullable=False)
    metodopago = db.Column(db.String(50), nullable=True)
    fecha= db.Column(db.Date, default=db.func.current_date())
    descuento = db.Column(db.Numeric(5,2), nullable=True)
    estado= db.Column(db.String(20), default='Pendiente')

    # Definición de la clave foránea compuesta
    __table_args__ = (
        ForeignKeyConstraint(
            ['idcliente', 'idmembresia'],
            ['detallemembresia.idcliente', 'detallemembresia.idmembresia'],
            ondelete="CASCADE"
        ),
    )
    
    detalle_membresia = db.relationship("DetalleMembresia", backref="pagos")

    def __init__(self, idcliente, idmembresia, monto, metodopago = None, descuento=None, estado='Pendiente'):
        self.idcliente = idcliente
        self.idmembresia = idmembresia
        self.monto = monto
        self.metodopago = metodopago
        self.descuento = descuento
        self.estado = estado

    def __repr__(self):
        return (f'<Pago(idpago={self.idpago}, idcliente={self.idcliente}, '
                f'idmembresia={self.idmembresia}, monto={self.monto}, '
                f'metodopago={self.metodopago}, fecha={self.fecha}, '
                f'descuento={self.descuento}, estado={self.estado})>')
