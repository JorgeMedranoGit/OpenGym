from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.proveedores import Proveedores
from database import db


proveedores_blueprint = Blueprint('proveedores_blueprint', __name__)

@proveedores_blueprint.route("/proveedores", methods=["GET"])
def verProveedores():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    return render_template("proveedores/verProveedores.html", proveedores=Proveedores.query.filter(Proveedores.habilitado == True).all())
@proveedores_blueprint.route("/verProveedoresDeshabilitados", methods=["GET"])
def verProveedoresDeshabilitados():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    return render_template("proveedores/proveedoresDesh.html", proveedores=Proveedores.query.filter(Proveedores.habilitado == False).all())
@proveedores_blueprint.route("/addProveedores", methods=["POST", "GET"])
def proveedoresCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
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
    return render_template("proveedores/proveedores.html")
#Proveedores (Edicion)
@proveedores_blueprint.route("/proveedores/editar/<int:id>", methods=["GET"])
def editarProveedor(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    proveedor = Proveedores.query.get(id) 
    return render_template("proveedores/proveedores.html", proveedor=proveedor)

@proveedores_blueprint.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def eliminarProveedor(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    proveedor = Proveedores.query.get(id)
    if proveedor:
        proveedor.habilitado = False
        db.session.commit()  # Guarda los cambios en la base de datos
        flash("Proveedor deshabilitado exitosamente!")
    else:
        flash("Proveedor no encontrado.")
    return redirect("/proveedores")
@proveedores_blueprint.route("/proveedores/habilitar/<int:id>", methods=["POST"])
def habilitarProveedor(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    proveedor = Proveedores.query.get(id)
    if proveedor:
        proveedor.habilitado = True
        db.session.commit()  # Guarda los cambios en la base de datos
        flash("Proveedor habilitado exitosamente!")
    else:
        flash("Proveedor no encontrado.")
    return redirect("/proveedores")


@proveedores_blueprint.route("/proveedores/buscar", methods=["GET"])
def buscarProveedores():
    if "email" not in session:
        return jsonify([])  # Retorna una lista vacía si no hay sesión
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    nombre = request.args.get('nombre', '')
    proveedores = Proveedores.query.filter(Proveedores.nombre.ilike(f'%{nombre}%')).all()  # Filtra por nombre

    # Convertir los resultados a un formato JSON
    resultados = [{'id': proveedor._id, 'nombre': proveedor.nombre} for proveedor in proveedores]
    
    return jsonify(resultados)  # Retorna los resultados en formato JSON

def obtenerTodoslosProveedores():
    return Proveedores.query.filter(Proveedores.habilitado == True).all()

