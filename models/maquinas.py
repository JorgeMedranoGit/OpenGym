from database import db

class Maquinas(db.Model):
    __tablename__ = 'maquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("idmaquina", db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    idnombremaquina = db.Column(db.Integer, nullable=False)
    iddetallecompramaquina = db.Column(db.Integer, nullable=False)
    
    