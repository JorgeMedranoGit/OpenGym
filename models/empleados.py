from database import db

class Empleado(db.Model):
    __tablename__ = 'empleados'

    idempleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=True)
    carnet = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    sueldo = db.Column(db.Numeric(10, 2), nullable=True)
    cambiopassword = db.Column(db.Boolean, nullable=True)

    idrol = db.Column(db.Integer, db.ForeignKey('roles.idrol'), nullable=True)
    rol = db.relationship('Rol', backref='empleados')
    
    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'

class Rol(db.Model):
    __tablename__ = 'roles'

    idrol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Rol {self.descripcion}>'