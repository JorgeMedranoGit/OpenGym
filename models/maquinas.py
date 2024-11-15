from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from database import db


Base = declarative_base()



class Maquinas(db.Model):
    __tablename__ = 'maquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("idmaquina", db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)  # Nombre del producto
    estado = db.Column(db.String(50), nullable=False)  # Precio de venta, tipo decimal
    idnombremaquina = db.Column(db.Integer, nullable=False)
    idempleado = db.Column(db.Integer, nullable=False)  # Stock disponible
    idproveedor = db.Column(db.Integer, nullable=False)

    def __init__(self, tipo, estado, idnombremaquina, idempleado, idproveedor):
        self.tipo = tipo
        self.estado = estado
        self.idnombremaquina = idnombremaquina
        self.idempleado = idempleado
        self.idproveedor = idproveedor
    def __repr__(self):
        return f'<Maquina {self.idnombremaquina}, Tipo: {self.tipo}, Estado: {self.estado}, IdEmpleado: {self.idempleado}>'
    