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
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))    
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
                if(found_user.cambiopassword == False):
                    return render_template("password.html", empleado=found_user)
                flash("Inicio de sesión correcto" )
                session["email"] = found_user.email
                session["usuario"] = found_user.nombre + " " +  found_user.apellido
                session["empleado_id"] = found_user.idempleado
                flash("Inicio de sesión correcto" )

                return redirect("/")
            else:
                flash("Contraseña incorrecta")
                return redirect("login") 
        else:
            flash("Usuario no encontrado")
            return redirect("login") 

    else:
        if "email" in session: 
            flash("Ya iniciaste sesión!")
            return redirect(url_for("main_blueprint.home"))

    return render_template("login.html")




@main_blueprint.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("nombre", None)
    session.pop("email", None)
    session.pop("empleado_id", None)
    return redirect("login")


@main_blueprint.route("/inicio")
def inicio():
    return render_template("inicio.html")


@main_blueprint.route("/password", methods=["POST"])
def password():
    if request.method == "POST":
        idemp = request.form["idemp"]
        passw = request.form["pass1"]
        emp = Empleado.query.get(idemp) 
        
        if emp:
            hashed_password = generate_password_hash(passw)
            
            emp.password = hashed_password
            
            emp.cambiopassword = True
            
            db.session.commit()
            session["email"] = emp.email
            session["usuario"] = emp.nombre + " " +  emp.apellido
            session["idempleado"] = emp.idempleado
            flash("Contraseña cambiada con éxito", "success")
            return redirect(url_for("main_blueprint.home"))
        else:
            flash("Empleado no encontrado", "danger")
            return redirect(url_for("main_blueprint.login"))

