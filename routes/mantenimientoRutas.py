from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from models.mantenimientoMaquina import MantenimientoMaquina
from models.empleados import Empleado
from models.maquinas import Maquinas
from models.nombreMaquina import NombreMaquinas
from database import db
from datetime import datetime, timedelta

mantenimiento_bp = Blueprint('mantenimiento', __name__)

@mantenimiento_bp.route('/mantenimientos', methods=['GET'])
def listar_maquinas():
    maquinas = Maquinas.query.all()
    return render_template('/mantenimiento/mantenimiento.html', maquinas=maquinas)

@mantenimiento_bp.route('/asignar_mantenimiento/<int:id>', methods=['GET', 'POST'])
def asignar_mantenimiento(id):
    maquina = Maquinas.query.get_or_404(id)
    empleados = Empleado.query.all()  # Asume que tienes una tabla de empleados
    if request.method == 'POST':
        # Obtener datos del formulario
        fechainicio = request.form['fechainicio']
        fechafin = request.form['fechafin']
        idempleado = request.form['idempleado']
        tipo = request.form['tipo']

        # Crear un nuevo registro de mantenimiento
        nuevo_mantenimiento = MantenimientoMaquina(
            idmaquina=maquina._id,
            tipo=maquina.tipo,
            estado="En mantenimiento",
            idempleado=idempleado,
            fechainicio=fechainicio,
            fechafin=fechafin,
        )

        db.session.add(nuevo_mantenimiento)
        db.session.commit()
        flash("Mantenimiento asignado exitosamente", "success")
        return redirect(url_for('mantenimiento.listar_maquinas'))
    return render_template('/mantenimiento/crearMaquina.html', maquina=maquina, empleados=empleados)


