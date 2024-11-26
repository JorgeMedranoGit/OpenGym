from flask import Blueprint, redirect, render_template, request, session, flash, url_for
from datetime import timedelta, date, datetime
from models.sesiones import Sesion
from models.pagos import Pago
from models.clientes import Clientes
from models.membresias import Membresias
from models.detalleMembresia import DetalleMembresia
from sqlalchemy import desc, text, and_, func
from database import db

pago_blueprint = Blueprint('pago_blueprint', __name__)

@pago_blueprint.route("/pago_reporte", methods=["POST", "GET"])
def reporte_pago():
    if "email" not in session:
        flash("Debes iniciar sesión", "warning")
        return redirect(url_for("main_blueprint.login"))

    rol = session.get('rol')
    idempleado = session.get('empleado_id')

    # Filtros de fecha
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')

    try:
        if request.method == "POST" and fecha_inicio and fecha_fin:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

                # Validar el orden lógico de fechas
                if fecha_inicio > fecha_fin:
                    flash("La fecha de inicio no puede ser posterior a la fecha de fin.", "danger")
                    return redirect(url_for("pago_blueprint.reporte_pago"))

            except ValueError:
                flash("Por favor, ingresa fechas válidas en formato YYYY-MM-DD.", "danger")
                return redirect(url_for("pago_blueprint.reporte_pago"))
        else:
            # Rango predeterminado si no se proporcionan fechas
            fecha_inicio = fecha_fin = date.today()

        # Base de filtros
        filtros = [Pago.fecha.between(fecha_inicio, fecha_fin)]
        if rol == 'recepcionista':
            filtros.append(Pago.idempleado == idempleado)

        # Consultar pagos en el rango
        pagos = (
            db.session.query(
                Pago.idpago,
                Pago.fecha,
                Pago.monto,
                Pago.metodopago,
                Pago.estado,
                Membresias.tipomembresia,
                Clientes.nombre,
                Clientes.apellido
            )
            .join(Clientes, Pago.idcliente == Clientes.idcliente)
            .outerjoin(Membresias, Pago.idmembresia == Membresias.idmembresia)
            .filter(and_(*filtros))
            .order_by(desc(Pago.fecha))
            .all()
        )

        # Total por tipo de membresía en el rango de fechas
        pagos_hoy = (
            db.session.query(
                Membresias.tipomembresia,
                func.sum(Pago.monto).label('total'),
                func.count(Pago.idpago).label('cantidad')
            )
            .outerjoin(Membresias, Pago.idmembresia == Membresias.idmembresia)
            .filter(and_(*filtros))
            .group_by(Membresias.tipomembresia)
            .all()
        )

        # Total por cliente en el rango de fechas (solo para administrador)
        pagos_por_cliente = []
        if rol == 'administrador':
            pagos_por_cliente = (
                db.session.query(
                    Clientes.nombre,
                    Clientes.apellido,
                    func.sum(Pago.monto).label('total')
                )
                .join(Clientes, Pago.idcliente == Clientes.idcliente)
                .filter(and_(*filtros))
                .group_by(Clientes.nombre, Clientes.apellido)
                .all()
            )

        # Total general en el rango de fechas
        total_general = sum([pago.monto for pago in pagos])

        return render_template(
            "pagos_membresias.html",
            pagos=pagos,
            pagos_hoy=pagos_hoy,
            pagos_por_cliente=pagos_por_cliente,
            total_general=total_general,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            rol=rol
        )
    except Exception as e:
        flash(f"Error al cargar los reportes de pagos: {str(e)}", "danger")
        return redirect(url_for("main_blueprint.home"))
