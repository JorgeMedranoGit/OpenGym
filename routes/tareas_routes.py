# routes/tareas.py
from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from models.tareas import Tarea
from models.empleados import Empleado
from database import db

tareas_blueprint = Blueprint('tareas_blueprint', __name__)


@tareas_blueprint.route('/tareas', methods=['GET', 'POST'])
def tareas_crud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    if request.method == 'POST':
        tarea_id = request.form.get('tarea_id')
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        idempleado = request.form.get('idempleado')
        
        if tarea_id:
            actualizar_tarea(tarea_id, titulo, descripcion, idempleado)
            flash('Tarea actualizada correctamente')
        else:
            agregar_tarea(titulo, descripcion, idempleado)
            flash('Tarea añadida correctamente')
        
        return redirect('/tareas')

    tareas = obtener_todas_las_tareas()
    empleados = obtener_todos_los_empleados()
    return render_template('tareas/tareas.html', tareas=tareas, empleados=empleados, rol = session["rol"])


@tareas_blueprint.route('/tareas/editar/<int:tarea_id>', methods=['GET'])
def editar_tarea(tarea_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    tarea = obtener_tarea_por_id(tarea_id)
    empleados = obtener_todos_los_empleados()
    return render_template('tareas/editar_tarea.html', tarea=tarea, empleados=empleados, rol = session["rol"])


@tareas_blueprint.route('/tareas/eliminar/<int:tarea_id>', methods=['POST'])
def eliminar_tarea(tarea_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    eliminar_tarea_por_id(tarea_id)
    flash('Tarea eliminada correctamente')
    return redirect('/tareas')


@tareas_blueprint.route('/tareas/comentarios', methods=['GET'])
def ver_comentarios():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    # Obtener todas las tareas, cada una con su comentario
    tareas = Tarea.query.all()
    return render_template('tareas/comentarios.html', tareas=tareas, rol = session["rol"])




def obtener_todas_las_tareas():
    return Tarea.query.all()

def obtener_tarea_por_id(tarea_id):
    return Tarea.query.get(tarea_id)

def agregar_tarea(titulo, descripcion, idempleado=None):
    nueva_tarea = Tarea(titulo=titulo, descripcion=descripcion, idempleado=idempleado)
    db.session.add(nueva_tarea)
    db.session.commit()

def actualizar_tarea(tarea_id, titulo, descripcion, idempleado=None):
    tarea = Tarea.query.get(tarea_id)
    tarea.titulo = titulo
    tarea.descripcion = descripcion
    tarea.idempleado = idempleado
    db.session.commit()

def eliminar_tarea_por_id(tarea_id):
    tarea = Tarea.query.get(tarea_id)
    db.session.delete(tarea)
    db.session.commit()

def obtener_todos_los_empleados():
    return Empleado.query.all()
