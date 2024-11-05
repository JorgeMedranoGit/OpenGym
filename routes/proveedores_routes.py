from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.proveedores import Proveedores
from database import db


proveedores_blueprint = Blueprint('proveedores_blueprint', __name__)

@proveedores_blueprint.route("/proveedores", methods=["POST", "GET"])
def proveedoresCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if request.method == "POST":
        nombre = request.form['nombreProveedor']
        telefono = request.form['telefonoProveedor']  
        correo = request.form['correoProveedor']
        proveedor_id = request.form.get('proveedor_id')  
        if proveedor_id: 
            proveedor = Proveedores.query.get(proveedor_id)
            proveedor.nombre = nombre
            proveedor.telefono = telefono
            proveedor.correo = correo
            db.session.commit() 
            flash("Proveedor editado exitosamente!")
        else:
            nuevo_proveedor = Proveedores(nombre, telefono, correo)
            db.session.add(nuevo_proveedor)
            db.session.commit() 
            flash("Proveedor añadido exitosamente!")
        return redirect("/proveedores")
    proveedores = Proveedores.query.all()
    return render_template("proveedores.html", proveedores=proveedores)
#Proveedores (Edicion)
@proveedores_blueprint.route("/proveedores/editar/<int:id>", methods=["GET"])
def editarProveedor(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    proveedor = Proveedores.query.get(id) 
    return render_template("proveedores.html", proveedor=proveedor, proveedores=Proveedores.query.all())

@proveedores_blueprint.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def eliminarProveedor(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    proveedor = Proveedores.query.get(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash("Proveedor eliminado exitosamente!")
    return redirect("/proveedores")

def obtenerTodoslosProveedores():
    return Proveedores.query.all()

