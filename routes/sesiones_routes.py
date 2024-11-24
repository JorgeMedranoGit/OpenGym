from flask import Blueprint, redirect, render_template, request, session, flash, url_for
from datetime import timedelta, date, datetime
from models.sesiones import Sesion
from models.pagos import Pago
from models.clientes import Clientes
from models.membresias import Membresias
from models.detalleMembresia import DetalleMembresia
from sqlalchemy import and_,desc,text
from database import db

session_blueprint = Blueprint('session_blueprint', __name__)

# Ruta para gestionar sesiones
@session_blueprint.route("/session", methods=["POST", "GET"])
def sessionCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    if request.method == "POST":
        tipo_sesion = request.form.get('tipo_sesion')
        idempleado = session['empleado_id'] 

        if not tipo_sesion:
            flash("Por favor selecciona un tipo de sesión.")
            return redirect(url_for("session_blueprint.sessionCrud"))

        try:
            if tipo_sesion == 'visita':
                costo = request.form.get('costo', type=float)
                metodo_pago = request.form.get('metodo_pago')

                if not costo or not metodo_pago:
                    flash("Por favor proporciona todos los datos para registrar la visita.")
                    return redirect(url_for("session_blueprint.sessionCrud"))
                
                id_cliente_generico = 27  # Cliente genérico
                nuevo_pago = Pago(
                    monto=costo,
                    metodopago=metodo_pago,
                    estado='Pendiente',
                    idcliente=id_cliente_generico,
                    idmembresia=None
                )
                db.session.add(nuevo_pago)
                db.session.flush()

                sesion = Sesion(
                    tipo_sesion='visita',
                    costo=costo,
                    idempleado=idempleado,
                    idpago=nuevo_pago.idpago
                )
                db.session.add(sesion)
                db.session.commit()
                flash("Sesión de visita registrada correctamente.")

            elif tipo_sesion == 'miembro':
                idcliente = request.form.get('idcliente', type=int)

                if not idcliente:
                    flash("Por favor selecciona un cliente válido para registrar la asistencia.")
                    return redirect(url_for("session_blueprint.sessionCrud"))

                sesion = Sesion(
                    tipo_sesion='miembro',
                    idcliente=idcliente,
                    idempleado=idempleado,
                    costo=0.00,
                    idpago=None
                )
                db.session.add(sesion)
                db.session.commit()
                flash("Asistencia de miembro registrada correctamente.")

            else:
                flash("Tipo de sesión inválido.")
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar la sesión: {str(e)}")

        return redirect(url_for("session_blueprint.sessionCrud"))

    return render_template("session.html", rol = session["rol"])

@session_blueprint.route("/cliente_card/<int:id>", methods=["GET", "POST"])
def ver_cliente(id):
    try:
        # Obtener el cliente
        cliente = Clientes.query.get(id)
        if not cliente:
            flash("El cliente no existe", "danger")
            return redirect(url_for('main_blueprint.home'))

        # Consultar membresías vigentes usando la función de PostgreSQL
        query = text("SELECT * FROM obtener_membresias_vigentes(:id_cliente)")
        result = db.session.execute(query, {'id_cliente': id})
        
        # Convertir los resultados a una lista de tuplas
        membresias = result.fetchall()  # Devuelve resultados como filas individuales

        # Consultar asistencias del cliente
        asistencias = (
            Sesion.query
            .filter(Sesion.idcliente == id)
            .order_by(desc(Sesion.fechasesion))
            .all()
        )

        # Determinar si hay membresías vencidas
        membresia_vencida = len(membresias) == 0  # True si no hay membresías vigentes

        # Verificar si el cliente puede registrar asistencia
        puede_registrar_asistencia = False
        if not membresia_vencida:
            fecha_vencimiento = membresias[0][2] 
            hoy = date.today()
            puede_registrar_asistencia = hoy <= fecha_vencimiento

        return render_template(
            'asistenciaCliente.html',
            cliente=cliente,
            membresia_vencida=membresia_vencida,
            membresias=membresias,
            asistencias=asistencias,
            puede_registrar_asistencia=puede_registrar_asistencia
        )
    except Exception as e:
        flash(f"Error al cargar los datos del cliente: {str(e)}", "danger")
        return redirect(url_for('session_blueprint.sessionCrud'))

# Ruta para renovar membresías
@session_blueprint.route("/clientes/<int:id>/renovar", methods=["GET", "POST"])
def renovar_membresia(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))
    
    cliente = Clientes.query.get(id)
    if not cliente:
        flash("Cliente no encontrado", "danger")
        return redirect(url_for("cliente_blueprint.clientesCrud"))

    # Verificar si la membresía está vencida
    query = text("SELECT * FROM obtener_membresias_vigentes(:id_cliente)")
    result = db.session.execute(query, {'id_cliente': id})
    membresias = result.fetchall()

    if not membresias:
        flash("El cliente no tiene una membresía activa o vigente para renovar.", "danger")
        return redirect(url_for("session_blueprint.ver_cliente", id=id))

    membresia_vencida = max(membresias, key=lambda m: m['fechavencimiento'])
    
    if membresia_vencida['fechavencimiento'] >= datetime.now().date():
        flash("La membresía aún está activa. No es necesario renovarla.", "danger")
        return redirect(url_for("session_blueprint.ver_cliente", id=id))
    
    if request.method == "POST":
        idmembresia = request.form.get("idmembresia", type=int)
        membresia = Membresias.query.get(idmembresia)

        if not membresia:
            flash("Membresía no válida", "danger")
            return redirect(url_for("session_blueprint.ver_cliente", id=id))

        try:
            # Gestionar detalle de membresía
            detalle_membresia = (
                cliente.detallemembresia[0] if cliente.detallemembresia else None
            )
            if not detalle_membresia:
                detalle_membresia = DetalleMembresia(
                    idcliente=cliente.idcliente,
                    idmembresia=membresia.idmembresia,
                    fechainicio=date.today(),
                    fechavencimiento=date.today() + timedelta(days=membresia.duracion)
                )
                db.session.add(detalle_membresia)
            else:
                detalle_membresia.fechavencimiento = max(
                    detalle_membresia.fechavencimiento or date.today(),
                    date.today()
                ) + timedelta(days=membresia.duracion)


            cliente.activo = True

            # Crear un registro de pago
            nuevo_pago = Pago(
                idcliente=id,
                idmembresia=membresia.idmembresia,
                monto=membresia.costo,
                metodopago="Pendiente",
                estado="Pendiente"
            )
            db.session.add(nuevo_pago)
            db.session.commit()

            flash(f"Membresía renovada hasta el {detalle_membresia.fechavencimiento}.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al renovar membresía: {str(e)}", "danger")

        return redirect(url_for("session_blueprint.ver_cliente", id=id))

    membresias = Membresias.query.filter_by(habilitado=True).all()
    return render_template("renovar_membresia.html", cliente=cliente, membresias=membresias)

@session_blueprint.route('/registrar_visita/<int:id_cliente>', methods=['POST'])
def registrar_visita(id_cliente):
    try:
        
        query = text("SELECT * FROM obtener_membresias_vigentes(:id_cliente)")
        result = db.session.execute(query, {'id_cliente': id_cliente})
        membresias = result.fetchall()

        if not membresias:
            flash("No se puede registrar la asistencia. No hay membresías vigentes.", "danger")
            return redirect(url_for('session_blueprint.ver_cliente', id=id_cliente))

        fecha_vencimiento = membresias[0][2] 
        hoy = date.today()
        if hoy > fecha_vencimiento:
            flash("No se puede registrar la asistencia. La membresía ha vencido.", "danger")
            return redirect(url_for('session_blueprint.ver_cliente', id=id_cliente))

        nueva_sesion = Sesion(
            tipo_sesion="miembro",
            idcliente=id_cliente,
            idempleado=session.get('empleado_id'),
            costo=0.00
        )
        db.session.add(nueva_sesion)
        db.session.commit()

        flash("Asistencia registrada exitosamente.", "success")
        return redirect(url_for('session_blueprint.ver_cliente', id=id_cliente))

    except Exception as e:
        flash(f"Error al registrar la asistencia: {str(e)}", "danger")
        return redirect(url_for('session_blueprint.ver_cliente', id=id_cliente))
    

@session_blueprint.route("/cliente_historial/<int:id>", methods=["GET"])
def historial_membresias(id):
    try:
        # Obtener el cliente
        cliente = Clientes.query.get(id)
        if not cliente:
            flash("El cliente no existe", "danger")
            return redirect(url_for('main_blueprint.home'))

        query = text("""
        SELECT m.tipomembresia, dm.fechainicio, dm.fechavencimiento, p.monto, p.fecha, p.estado
        FROM detallemembresia dm
        JOIN membresia m ON dm.idmembresia = m.idmembresia
        LEFT JOIN pago p ON p.idcliente = dm.idcliente AND p.idmembresia = dm.idmembresia
        WHERE dm.idcliente = :id_cliente
        ORDER BY dm.fechainicio DESC;
        """)

        result = db.session.execute(query, {'id_cliente': id})
        historial = result.fetchall() 
        return render_template('historial_membresias.html', cliente=cliente, historial=historial)
    
    except Exception as e:
        flash(f"Error al cargar el historial de membresías: {str(e)}", "danger")
        return redirect(url_for('session_blueprint.sessionCrud'))
    

@session_blueprint.route("/reporte_visitas", methods=["GET", "POST"])
def reporte_visitas():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    try:

        fecha_inicio = request.form.get("fecha_inicio")
        fecha_fin = request.form.get("fecha_fin")
        empleado_id = session.get("empleado_id")
        es_admin = session.get("rol") == "Administrador"

        hoy = date.today()
        filtros = [Sesion.fechasesion == hoy]

        if not es_admin:
            filtros.append(Sesion.idempleado == empleado_id)

        # Filtrar por rango de fechas (si se seleccionó)
        if fecha_inicio and fecha_fin:
            filtros = [Sesion.fechasesion.between(fecha_inicio, fecha_fin)]

        # Consultar sesiones con filtros
        visitas = (
            db.session.query(
                Sesion.idsesion,
                Sesion.tipo_sesion,
                Sesion.fechasesion,
                Sesion.costo,
                Clientes.nombre,
                Clientes.apellido,
                Membresias.tipomembresia,
                Sesion.idempleado,
            )
            .join(Clientes, Sesion.idcliente == Clientes.idcliente, isouter=True)
            .join(Pago, Sesion.idpago == Pago.idpago, isouter=True)
            .join(DetalleMembresia, (DetalleMembresia.idcliente == Sesion.idcliente), isouter=True)
            .join(Membresias, DetalleMembresia.idmembresia == Membresias.idmembresia, isouter=True)
            .filter(*filtros)
            .order_by(Sesion.fechasesion.desc())
            .all()
        )

        # Calcular resumen por tipo de sesión
        total_miembros = sum(1 for v in visitas if v.tipo_sesion == "miembro")
        total_visitas_regulares = sum(1 for v in visitas if v.tipo_sesion == "visita")

        return render_template(
            "reporte_visitas.html",
            visitas=visitas,
            total_miembros=total_miembros,
            total_visitas_regulares=total_visitas_regulares,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            es_admin=es_admin,
            rol = session["rol"],
        )
    except Exception as e:
        flash(f"Error al generar el reporte: {str(e)}", "danger")
        return redirect(url_for("session_blueprint.sessionCrud"))
