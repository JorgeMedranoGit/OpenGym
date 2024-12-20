from database import db

from sqlalchemy import update



class Maquinas(db.Model):
    __tablename__ = 'maquina'  # Nombre de la tabla en la base de datos

    _id = db.Column("idmaquina", db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    idnombremaquina = db.Column(db.Integer, nullable=False)
    iddetallecompramaquina = db.Column(db.Integer, nullable=False)
    
    def __init__(self, tipo, estado, idnombremaquina, iddetallecompramaquina):
        self.tipo = tipo
        self.estado = estado
        self.idnombremaquina = idnombremaquina
        self.iddetallecompramaquina = iddetallecompramaquina
    def __repr__(self):
        return f'<Maquina {self.idnombremaquina}, Tipo: {self.tipo}, Estado: {self.estado}, IdEmpleado: {self.idempleado}>'
    def actualizar_estado_maquinas(iddetallecompramaquina):
    # Define el query para actualizar el estado a 'Operativo'
        query = (
            update(Maquinas)
            .where(Maquinas.iddetallecompramaquina == iddetallecompramaquina)
            .values(estado='Operativo')
        )
        db.session.execute(query)
        db.session.commit()

    