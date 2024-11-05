from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.estados import Estados
from database import db


estados_blueprint = Blueprint('estados_blueprint', __name__)

def obtener_todos_los_estados():
    return Estados.query.all()


