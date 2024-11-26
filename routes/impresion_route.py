from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file
from datetime import datetime
from models.empleados import Empleado

impresion_blueprint = Blueprint('impresion_blueprint', __name__)

@impresion_blueprint.route("/imprimir", methods=['GET', 'POST'])
def impresion():
    if session.get('thead') and session.get('tbody'):
        # Obtener la fecha actual
        fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Suponiendo que tienes el ID del empleado en la sesión
        empleado_id = session.get('empleado_id')
        
        empleado = Empleado.query.get(empleado_id)

        empleado = empleado.nombre + ' '+ empleado.apellido

        # Para este ejemplo, supongamos que el nombre del empleado es "Juan Pérez"
        empleado_nombre = "Juan Pérez"  # Reemplaza esto con la consulta real

        if session.get('extra'):
            return render_template("imprimir.html", 
                                   claves=session['thead'],
                                   valores=session['tbody'],
                                   extra=session['extra'],
                                   fecha=fecha_reporte,
                                   empleado=empleado)
        return render_template("imprimir.html", 
                               claves=session['thead'],
                               valores=session['tbody'],
                               fecha=fecha_reporte,
                               empleado=empleado)
    
    flash("No se pueden realizar impresiones ahora mismo")
    return redirect('/')