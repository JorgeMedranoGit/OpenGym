from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.clientes import Clientes
from database import db

cliente_blueprint = Blueprint('cliente_blueprint', __name__)

@cliente_blueprint.route("/clientes", methods=["POST", "GET"])
def clientesCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if request.method == "POST":
        nombre = request.form['nombre_cliente']
        apellido = request.form['apellido_cliente']
        carnet = request.form['carnet_cliente']
        telefono = request.form['telefono_cliente']
        tipocliente = request.form['tipocliente_cliente']
        cliente_id = request.form.get('cliente_id')  
        #Editar cliente
        if cliente_id:
            cliente = Clientes.query.get(cliente_id)
            cliente.nombre = nombre
            cliente.apellido = apellido
            cliente.carnet = carnet
            cliente.telefono = telefono
            cliente.tipocliente = tipocliente
            db.session.commit()
            flash("Cliente editado exitosamente!")
        else:  
            nuevo_cliente = Clientes(nombre, apellido, carnet, telefono, tipocliente)
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash("Cliente añadido exitosamente!")
        return redirect("/clientes")
    # Obtener datos
    clientes = Clientes.query.all()
    return render_template("clientes.html", clientes=clientes)


@cliente_blueprint.route("/clientes/editar/<int:id>", methods=["GET"])
def editarCliente(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    cliente = Clientes.query.get(id)
    return render_template("clientes.html", cliente=cliente, clientes=Clientes.query.all())
 
@cliente_blueprint.route("/clientes/eliminar/<int:id>", methods=["POST"])
def eliminarCliente(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    cliente = Clientes.query.get(id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado exitosamente!")
    return redirect("/clientes")


def obtener_todos_los_clientes():
    return Clientes.query.all()