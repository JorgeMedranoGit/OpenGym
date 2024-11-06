from database import db

class Tarea(db.Model):
    __tablename__ = 'tareas'

    idtarea = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.Boolean, default=False)  # False = pendiente, True = completada
    idempleado = db.Column(db.Integer, db.ForeignKey('empleados.idempleado'), nullable=True)
    comentario = db.Column(db.Text)

    empleado = db.relationship('Empleado', backref='tareas')

    def __repr__(self):
        return f'<Tarea {self.titulo} - {"Completada" if self.estado else "Pendiente"}>'
