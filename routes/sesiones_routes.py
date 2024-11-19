from flask import Blueprint, redirect, render_template, request, session, flash, url_for
from models.sesiones import Sesion
from models.pagos import Pago
from models.clientes import Clientes
from database import db

session_blueprint = Blueprint('session_blueprint', __name__)

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
                
                id_cliente_generico=1
                nuevo_pago = Pago(
                    monto=costo,
                    metodopago=metodo_pago,
                    estado='Pendiente',
                    idcliente=id_cliente_generico,
                    idmembresia=None
                )
                db.session.add(nuevo_pago)
                db.session.flush()

                # Registrar una sesión de visita
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

                # Registrar la asistencia de un miembro
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

    return render_template("session.html")

@session_blueprint.route("/clientes/<int:id>", methods=["GET", "POST"])
def ver_cliente(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    cliente = Clientes.query.get(id)
    if not cliente:
        flash("Cliente no encontrado")
        return redirect(url_for("cliente_blueprint.clientesCrud"))

    if request.method == "POST":
        # Cambiar el estado del cliente (activo/inactivo)
        nuevo_estado = not cliente.activo  # Cambia entre True y False
        cliente.activo = nuevo_estado
        db.session.commit()

        estado = "activo" if cliente.activo else "inactivo"
        flash(f"El cliente ha sido marcado como {estado}.")
        return redirect(url_for("session_blueprint.ver_cliente", id=id))

    # Obtener sesiones relacionadas con el cliente
    sesiones = Sesion.query.filter_by(idcliente=id).all()

    return render_template("ver_cliente.html", cliente=cliente, sesiones=sesiones)