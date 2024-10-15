from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.empleados import Empleado
from database import db


empleados_blueprint = Blueprint('empleados_blueprint', __name__)

@empleados_blueprint.route('/empleados', methods=['GET', 'POST'])
def empleadosCrud():
    if request.method == 'POST':
        empleado_id = request.form.get('empleado_id')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        direccion = request.form.get('direccion')
        carnet = request.form.get('carnet')
        telefono = request.form.get('telefono')
        sueldo = request.form.get('sueldo')
        
        if empleado_id:  # Actualizar empleado
            actualizar_empleado(empleado_id, nombre, apellido, direccion, carnet, telefono, sueldo)
            flash('Empleado actualizado correctamente')
        else:  # Agregar nuevo empleado
            agregar_empleado(nombre, apellido, direccion, carnet, telefono, sueldo)
            flash('Empleado añadido correctamente')
        
        return redirect('/empleados')

    empleados = obtener_todos_los_empleados()
    return render_template('empleados.html', empleados=empleados)


@empleados_blueprint.route('/empleados/editar/<int:empleado_id>', methods=['GET'])
def editar_empleado(empleado_id):
    empleado = obtener_empleado_por_id(empleado_id)
    return render_template('empleados.html', empleado=empleado, empleados=obtener_todos_los_empleados())


@empleados_blueprint.route('/empleados/eliminar/<int:empleado_id>', methods=['POST'])
def eliminar_empleado(empleado_id):
    eliminar_empleado_por_id(empleado_id)
    flash('Empleado eliminado correctamente')
    return redirect('/empleados')


def obtener_todos_los_empleados():
    return Empleado.query.all()

def obtener_empleado_por_id(empleado_id):
    return Empleado.query.get(empleado_id)

def agregar_empleado(nombre, apellido, direccion, carnet, telefono, sueldo):
    nuevo_empleado = Empleado(nombre=nombre, apellido=apellido, direccion=direccion, carnet=carnet, telefono=telefono, sueldo=sueldo)
    db.session.add(nuevo_empleado)
    db.session.commit()

def actualizar_empleado(empleado_id, nombre, apellido, direccion, carnet, telefono, sueldo):
    empleado = Empleado.query.get(empleado_id)
    empleado.nombre = nombre
    empleado.apellido = apellido
    empleado.direccion = direccion
    empleado.carnet = carnet
    empleado.telefono = telefono
    empleado.sueldo = sueldo
    db.session.commit()

def eliminar_empleado_por_id(empleado_id):
    empleado = Empleado.query.get(empleado_id)
    db.session.delete(empleado)
    db.session.commit()

