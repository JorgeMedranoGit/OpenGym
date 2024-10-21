from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

from database import db

# Importar db desde app.py



Base = declarative_base()

class Rol(db.Model):
    __tablename__ = 'roles'

    idrol = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Rol {self.descripcion}>'