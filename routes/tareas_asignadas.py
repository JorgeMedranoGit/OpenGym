from flask import Blueprint, render_template, request, session, flash, redirect
from models.tareas import Tarea  # Asumimos que tienes una clase Tarea en models/tareas.py
from database import db

tareas_asignadas_blueprint = Blueprint('tareas_asignadas_blueprint', __name__)

# Ruta para ver las tareas asignadas al empleado
@tareas_asignadas_blueprint.route('/tareasCom', methods=['GET'])
def ver_tareas():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    # Obtén el empleado_id desde la sesión para filtrar las tareas
    empleado_id = session.get('empleado_id')

    # Recuperar las tareas del empleado autenticado
    tareas = Tarea.query.filter_by(idempleado=empleado_id).all()
    
    return render_template('tareas_asignadas/tareas.html', tareas=tareas)


# Ruta para marcar una tarea como completada
@tareas_asignadas_blueprint.route('/tareas/completar/<int:tarea_id>', methods=['POST'])
def completar_tarea(tarea_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    # Obtener la tarea por su ID
    tarea = Tarea.query.get(tarea_id)

    if tarea:
        # Marcar la tarea como completada (actualizar el estado)
        tarea.estado = True

        # Obtener el comentario del formulario, si existe
        comentario = request.form.get('comentario')

        if comentario:
            # Si el comentario existe, lo agregamos a la tarea
            tarea.comentario = comentario

        # Guardamos los cambios en la base de datos
        db.session.commit()

        flash("Tarea completada correctamente")
    else:
        flash("La tarea no existe")
    
    return redirect('/tareasCom')