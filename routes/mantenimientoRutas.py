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
    # Obtener todas las máquinas únicas con su último mantenimiento
    maquinas = db.session.query(
        Maquinas,
        MantenimientoMaquina.estado.label('mantenimiento_estado'),
        Empleado.nombre.label('empleado_nombre'),
        MantenimientoMaquina.fechainicio.label('fecha_inicio'),
        MantenimientoMaquina.fechafin.label('fecha_fin')
    ).outerjoin(
        MantenimientoMaquina, MantenimientoMaquina.idmaquina == Maquinas._id
    ).outerjoin(
        Empleado, Empleado.idempleado == MantenimientoMaquina.idempleado
    ).distinct(Maquinas._id).order_by(Maquinas._id).all()

    return render_template('/mantenimiento/mantenimiento.html', maquinas=maquinas, datetime=datetime, rol = session["rol"])

@mantenimiento_bp.route('/asignar_mantenimiento/<int:id>', methods=['GET', 'POST'])
def asignar_mantenimiento(id):
    maquina = Maquinas.query.get_or_404(id)
    empleados = Empleado.query.all()

    # Verificar si la máquina tiene un mantenimiento activo
    mantenimiento_actual = MantenimientoMaquina.query.filter_by(idmaquina=maquina._id).order_by(MantenimientoMaquina.fechafin.desc()).first()

    # Verificar si el estado de la máquina es "Finalizado" antes de asignar un nuevo mantenimiento
    if mantenimiento_actual and mantenimiento_actual.estado != "Finalizado":
        flash("La máquina debe estar en estado 'Finalizado' para asignar un nuevo mantenimiento.", "danger")
        return redirect(url_for('mantenimiento.listar_maquinas'))

    # Si hay mantenimiento activo, verificar las fechas
    if mantenimiento_actual:
        if mantenimiento_actual.fechafin >= datetime.today().date():
            flash("La máquina ya tiene un mantenimiento activo. No se puede asignar otro.", "danger")
            return redirect(url_for('mantenimiento.listar_maquinas'))

        # Verificar que la fecha de inicio del nuevo mantenimiento sea posterior a la fecha de fin del mantenimiento anterior
        if request.method == 'POST':
            fechainicio = datetime.strptime(request.form['fechainicio'], '%Y-%m-%d').date()
            if fechainicio <= mantenimiento_actual.fechafin: 
                flash("La fecha de inicio del mantenimiento debe ser posterior a la fecha de fin del mantenimiento anterior.", "danger")
                return redirect(url_for('mantenimiento.asignar_mantenimiento', id=maquina._id))

    # Validación del formulario antes de crear el mantenimiento
    if request.method == 'POST':
        # Obtener datos del formulario
        fechainicio = request.form.get('fechainicio')
        fechafin = request.form.get('fechafin')
        idempleado = request.form.get('idempleado')
        tipo = request.form.get('tipo')

        # Validar si el campo 'idempleado' está vacío
        if not idempleado:
            flash("Debe seleccionar un empleado para el mantenimiento.", "danger")
            return redirect(url_for('mantenimiento.asignar_mantenimiento', id=maquina._id))

        # Validar las fechas
        try:
            fechainicio = datetime.strptime(fechainicio, '%Y-%m-%d')
            fechafin = datetime.strptime(fechafin, '%Y-%m-%d')
        except ValueError:
            flash("Las fechas deben tener el formato adecuado (YYYY-MM-DD).", "danger")
            return redirect(url_for('mantenimiento.asignar_mantenimiento', id=maquina._id))

        # Validar que la fecha de inicio no sea antes de hoy
        if fechainicio.date() < datetime.today().date():
            flash("La fecha de inicio no puede ser anterior a la fecha actual.", "danger")
            return redirect(url_for('mantenimiento.asignar_mantenimiento', id=maquina._id))

        # Validar que la fecha de fin no sea anterior a la de inicio
        if fechafin.date() < fechainicio.date():
            flash("La fecha de fin no puede ser anterior a la fecha de inicio.", "danger")
            return redirect(url_for('mantenimiento.asignar_mantenimiento', id=maquina._id))

        # Crear un nuevo registro de mantenimiento
        nuevo_mantenimiento = MantenimientoMaquina(
            idmaquina=maquina._id,
            tipo=tipo,
            estado="En mantenimiento",
            idempleado=idempleado,
            fechainicio=fechainicio,
            fechafin=fechafin,
        )

        db.session.add(nuevo_mantenimiento)
        db.session.commit()
        flash("Mantenimiento asignado exitosamente", "success")
        return redirect(url_for('mantenimiento.listar_maquinas'))

    return render_template('/mantenimiento/crearMaquina.html', maquina=maquina, empleados=empleados, rol = session["rol"])

@mantenimiento_bp.route('/finalizar_mantenimiento/<int:id>', methods=['POST'])
def finalizar_mantenimiento(id):
    # Buscar el último mantenimiento de la máquina
    mantenimiento_actual = MantenimientoMaquina.query.filter_by(idmaquina=id).order_by(MantenimientoMaquina.fechafin.desc()).first()

    if mantenimiento_actual:
        # Actualizar el estado del mantenimiento
        mantenimiento_actual.estado = "Finalizado"

        # Actualizar el estado de la máquina a "En uso"
        maquina = Maquinas.query.get_or_404(id)
        maquina.estado = "En uso"

        db.session.commit()
        flash("Mantenimiento finalizado y máquina marcada como en uso.", "success")
    else:
        flash("No se encontró mantenimiento activo para esta máquina.", "danger")

    return redirect(url_for('mantenimiento.listar_maquinas'))

@mantenimiento_bp.route('/detalles_mantenimiento/<int:id>', methods=['GET'])
def ver_detalles(id):
    # Obtener todos los mantenimientos de la máquina
    mantenimientos = MantenimientoMaquina.query.filter_by(idmaquina=id).all()
    maquina = Maquinas.query.get_or_404(id)

    return render_template('/mantenimiento/detalles.html', mantenimientos=mantenimientos, maquina=maquina, rol = session["rol"])
