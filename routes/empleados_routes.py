from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from models.empleados import Empleado
from database import db
from models.empleados import Rol
from werkzeug.security import generate_password_hash

empleados_blueprint = Blueprint('empleados_blueprint', __name__)

@empleados_blueprint.route('/empleados', methods=['GET', 'POST'])
def empleadosCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if request.method == 'POST':
        empleado_id = request.form.get('empleado_id')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        direccion = request.form.get('direccion')
        carnet = request.form.get('carnet')
        telefono = request.form.get('telefono')
        sueldo = request.form.get('sueldo')
        email = request.form.get('email')
        
        if empleado_id:  # Actualizar empleado
            actualizar_empleado(empleado_id, nombre, apellido, direccion, carnet, telefono, sueldo, email)
            flash('Empleado actualizado correctamente')
        else:  # Agregar nuevo empleado
            agregar_empleado(nombre, apellido, direccion, carnet, telefono, sueldo, email)
            flash('Empleado añadido correctamente')
        
        return redirect('/empleados')

    empleados = obtener_todos_los_empleados()
    return render_template('empleados.html', empleados=empleados, rol = session["rol"])


@empleados_blueprint.route('/empleados/editar/<int:empleado_id>', methods=['GET'])
def editar_empleado(empleado_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    empleado = obtener_empleado_por_id(empleado_id)
    return render_template('empleados.html', empleado=empleado, empleados=obtener_todos_los_empleados(), rol = session["rol"])


@empleados_blueprint.route('/empleados/eliminar/<int:empleado_id>', methods=['POST'])
def eliminar_empleado(empleado_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    eliminar_empleado_por_id(empleado_id)
    flash('Empleado eliminado correctamente')
    return redirect('/empleados')


def obtener_todos_los_empleados():
    return Empleado.query.all()

def obtener_empleado_por_id(empleado_id):
    return Empleado.query.get(empleado_id)

def agregar_empleado(nombre, apellido, direccion, carnet, telefono, sueldo, email):
    nuevo_empleado = Empleado(nombre=nombre, apellido=apellido, direccion=direccion, carnet=carnet, telefono=telefono, sueldo=sueldo, email=email, password=encriptar_contrasena_defecto(),cambiopassword=False)
    db.session.add(nuevo_empleado)
    db.session.commit()

def actualizar_empleado(empleado_id, nombre, apellido, direccion, carnet, telefono, sueldo, email):
    empleado = Empleado.query.get(empleado_id)
    empleado.nombre = nombre
    empleado.apellido = apellido
    empleado.direccion = direccion
    empleado.carnet = carnet
    empleado.telefono = telefono
    empleado.sueldo = sueldo
    empleado.email = email
    db.session.commit()

def eliminar_empleado_por_id(empleado_id):
    empleado = Empleado.query.get(empleado_id)
    db.session.delete(empleado)
    db.session.commit()

def obtener_todos_los_roles():
    return Rol.query.all()


@empleados_blueprint.route('/empleados/asignar_rol/<int:empleado_id>', methods=['GET', 'POST'])
def asignar_rol(empleado_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    empleado = obtener_empleado_por_id(empleado_id)

    if request.method == 'POST':
        idrol = request.form.get('idrol')
        empleado.idrol = idrol
        db.session.commit()
        flash('Rol asignado correctamente')
        return redirect('/empleados')

    roles = obtener_todos_los_roles()  # Aquí obtienes todos los roles
    return render_template('asignar_rol.html', empleado=empleado, roles=roles, rol = session["rol"])


@empleados_blueprint.route('/empleados/actualizar_rol/<int:empleado_id>', methods=['GET', 'POST'])
def actualizar_rol(empleado_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    empleado = obtener_empleado_por_id(empleado_id)
    
    if request.method == 'POST':
        idrol = request.form.get('idrol')
        empleado.idrol = idrol
        db.session.commit()
        flash('Rol actualizado correctamente')
        return redirect('/empleados')

    roles = obtener_todos_los_roles()
    return render_template('actualizar_rol.html', empleado=empleado, roles=roles, rol = session["rol"])



def encriptar_contrasena_defecto():
    return generate_password_hash("123456")





