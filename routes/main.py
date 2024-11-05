from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.empleados import Empleado
from database import db

main_blueprint = Blueprint('main_blueprint', __name__)


@main_blueprint.route("/")
def home():
    return render_template("index.html")

@main_blueprint.route("/login", methods=["POST", "GET"]) 
def login():
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        

        found_user = Empleado.query.filter_by(email=email).first()
        
        if found_user:
            if check_password_hash(found_user.password, password):
                session["email"] = found_user.email
                session["usuario"] = found_user.nombre + " " +  found_user.apellido
                flash("Inicio de sesión correcto" )
                return redirect("/")
            else:
                flash("Contraseña incorrecta"+ found_user.password + " " + generate_password_hash(password))
                return redirect("home")
        else:
            flash("Usuario no encontrado")
            return redirect("login") 

    else:
        if "email" in session: 
            flash("Ya iniciaste sesión!")
            return redirect("home")

    return render_template("login.html")




@main_blueprint.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("nombre", None)
    session.pop("email", None)
    return redirect("login")

@main_blueprint.route("/test")
def test():
    return render_template("new.html")

@main_blueprint.route("/inicio")
def inicio():
    return render_template("inicio.html")