from database import db
from datetime import datetime

class MantenimientoMaquina(db.Model):
    __tablename__ = 'mantenimientomaquina'
    idmantenimiento= db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    idmaquina = db.Column(db.Integer, db.ForeignKey('maquina.idmaquina'))
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado'))
    fechainicio = db.Column(db.Date, nullable=False)
    fechafin = db.Column(db.Date, nullable=False)  # Fecha de fin del mantenimiento

    empleado = db.relationship('Empleado', backref='mantenimientos')

    maquina = db.relationship('Maquinas', backref='mantenimientos', lazy=True)