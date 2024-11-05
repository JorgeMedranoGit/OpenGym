from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import db

Base = declarative_base()


class Estados(db.Model):
    __tablename__ = 'estados'
 
    idestado = db.Column("idestado", db.Integer, primary_key=True, autoincrement=True)
    estado = db.Column(db.String(50), nullable=False)

    def __init__(self, estado):
        self.estado = estado