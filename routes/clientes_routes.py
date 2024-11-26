from flask import Blueprint, redirect, url_for, render_template, request, jsonify, session, flash
from datetime import timedelta, date
from decimal import Decimal
from models.clientes import Clientes
from models.detalleMembresia import DetalleMembresia
from models.membresias import Membresias
from models.pagos import Pago
from models.sesiones import Sesion
from database import db
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import logging

cliente_blueprint = Blueprint('cliente_blueprint', __name__)

@cliente_blueprint.route("/clientes", methods=["POST", "GET"])
def clientesCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    if request.method == "POST":
        nombre = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        carnet = request.form['carnet'].strip()
        telefono = request.form['telefono'].strip()
        tipo_suscripcion = request.form['tipo_suscripcion']
        cliente_id = request.form.get('cliente_id') 

        errores = []
        if not nombre or len(nombre) < 3:
            errores.append("El nombre es obligatorio y debe tener al menos 3 caracteres.")
            flash("datos incorrectos")
        if not apellido or len(apellido) < 3:
            errores.append("El apellido es obligatorio y debe tener al menos 3 caracteres.")
            flash("datos incorrectos")
        if not carnet.isdigit() or not (7 <= len(carnet) <= 9):
            errores.append("El carnet debe ser un número de 7 a 9 dígitos.")
            flash("datos incorrectos")

        carnet_existente = Clientes.query.filter_by(carnet=carnet, activo=True).first()
        if carnet_existente and (not cliente_id or int(cliente_id) != carnet_existente.idcliente):
            errores.append("El carnet ya está registrado en otro cliente activo.")
            flash("El carnert ya ha sido registrado")
        if not telefono.isdigit() or len(telefono) != 8 :
            errores.append("El teléfono debe tener 8 digitos")
            flash("datos incorrectos")

        if errores:
            for error in errores:
                flash(error)
            return redirect(url_for("cliente_blueprint.clientesCrud"))

        if cliente_id and cliente_id.isdigit():
            cliente = Clientes.query.get(int(cliente_id))
            if cliente:
                # Editar cliente existente
                cliente.nombre = nombre
                cliente.apellido = apellido
                cliente.carnet = carnet
                cliente.telefono = telefono
                db.session.commit()
                flash("Cliente editado exitosamente!")
            else:
                flash("Cliente no encontrado. No se pudo editar.")
        else:
            # Crear nuevo cliente
            nuevo_cliente = Clientes(
                nombre=nombre,
                apellido=apellido,
                carnet=carnet,
                telefono=telefono,
                tipocliente="pendiente"
            )
            db.session.add(nuevo_cliente)
            db.session.commit()

            if tipo_suscripcion == "membresia":
                membresia_id = request.form.get("membresia_id")
                metodo_pago = request.form.get("metodo_pago")

                membresia_info = Membresias.query.filter_by(idmembresia=membresia_id, habilitado=True).first()
                if membresia_info:
                    nueva_membresia = DetalleMembresia(
                        idcliente=nuevo_cliente.idcliente,
                        idmembresia=membresia_id,
                        fechainicio=date.today(),
                        fechavencimiento=date.today() + timedelta(days=30)
                    )
                    db.session.add(nueva_membresia)
                    
                    monto = membresia_info.costo
                    nuevo_pago = Pago(
                        idcliente=nuevo_cliente.idcliente,
                        idmembresia=membresia_id,
                        monto=monto,
                        metodopago=metodo_pago,
                        estado="Pendiente" 
                    )
                    db.session.add(nuevo_pago)
                else:
                    flash("La membresía seleccionada no está activa.")
            elif tipo_suscripcion == "sesion":
                metodo_pago = request.form.get("metodo_pago", "efectivo")
                monto = Decimal("20.00")

                nuevo_pago = Pago(
                    idcliente=nuevo_cliente.idcliente,
                    idmembresia=None,
                    monto=monto,
                    metodopago=metodo_pago,
                    estado="Pendiente" 
                )
                db.session.add(nuevo_pago)

            db.session.commit()
            flash("Cliente registrado exitosamente!")

        return redirect(url_for("cliente_blueprint.clientesCrud"))

    clientes = db.session.query(
        Clientes,
        Membresias.tipomembresia,
        Pago.estado.label("estado_pago")
    ).outerjoin(
        DetalleMembresia, Clientes.idcliente == DetalleMembresia.idcliente
    ).outerjoin(
        Membresias, db.and_(
            DetalleMembresia.idmembresia == Membresias.idmembresia,
            Membresias.habilitado == True  # Filtrar solo membresías habilitadas
        )
    ).outerjoin(
        Pago, db.and_(
            Pago.idcliente == Clientes.idcliente,
            Pago.idmembresia == DetalleMembresia.idmembresia
        )
    ).filter(Clientes.activo == True, Clientes.nombre != 'Cliente').order_by(
        Clientes.idcliente.desc()
    ).all()


    clientes_inactivos = Clientes.query.filter_by(activo=False).all()

    membresias = Membresias.query.filter_by(habilitado=True).all()

    return render_template(
        "clientes.html", 
        clientes=clientes, 
        clientes_inactivos=clientes_inactivos, 
        membresias=membresias,
        rol = session["rol"]
    )

@cliente_blueprint.route("/clientes/editar/<int:id>", methods=["GET"])
def editarCliente(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    cliente = Clientes.query.get(id)
    if cliente:
        membresias = Membresias.query.all()
        clientes = db.session.query(
            Clientes,
            Membresias.tipomembresia,
            Pago.estado.label("estado_pago")
        ).outerjoin(
            DetalleMembresia, Clientes.idcliente == DetalleMembresia.idcliente
        ).outerjoin(
            Membresias, DetalleMembresia.idmembresia == Membresias.idmembresia
        ).outerjoin(
            Pago, db.and_(
                Pago.idcliente == Clientes.idcliente,
                Pago.idmembresia == DetalleMembresia.idmembresia
            )
        ).filter(Clientes.activo == True).all()

        clientes_inactivos = Clientes.query.filter_by(activo=False).all()

        return render_template(
            "clientes.html",
            cliente=cliente,
            clientes=clientes,
            clientes_inactivos=clientes_inactivos,
            membresias=membresias,
            rol = session["rol"]
        )
    else:
        flash("Cliente no encontrado")
        return redirect(url_for("cliente_blueprint.clientesCrud"))



@cliente_blueprint.route("/clientes/desactivar/<int:id>", methods=["POST"])
def desactivarCliente(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    cliente = Clientes.query.get(id)
    if cliente:
        cliente.activo = False
        db.session.commit()
        flash("Cliente desactivado exitosamente!")
    return redirect(url_for("cliente_blueprint.clientesCrud"))


@cliente_blueprint.route("/clientes/actualizar_estado_pago", methods=["POST"])
def actualizar_estado_pago():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))
    
    idcliente = request.form.get("idcliente")
    nuevo_estado = request.form.get("estado")
    
    pago = Pago.query.filter_by(idcliente=idcliente).first()
    if pago:
        pago.estado = nuevo_estado
        db.session.commit()
        flash("El estado de pago se ha actualizado correctamente.")
    else:
        flash("No se encontró un registro de pago para este cliente.")
    
    return redirect(url_for("cliente_blueprint.clientesCrud"))


@cliente_blueprint.route('/clientes/buscar', methods=['GET'])
def buscar_clientes():
    query = request.args.get("q", "").strip()
    if not query:
        return []

    clientes = Clientes.query.filter(
        (Clientes.nombre.ilike(f"%{query}%")) | 
        (Clientes.apellido.ilike(f"%{query}%"))
    ).all()

    resultados = [
        {"idcliente": cliente.idcliente, "nombre": cliente.nombre, "apellido": cliente.apellido}
        for cliente in clientes
    ]
    return jsonify(resultados)


@cliente_blueprint.route('/clientes/<int:id>', methods=["GET", "POST"])
def ver_cliente(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    cliente = Clientes.query.get(id)
    if not cliente:
        flash("Cliente no encontrado")
        return redirect(url_for("cliente_blueprint.clientesCrud"))

    if request.method == "POST":
        nuevo_estado = not cliente.activo 
        cliente.activo = nuevo_estado
        db.session.commit()

        estado = "activo" if cliente.activo else "inactivo"
        flash(f"El cliente ha sido marcado como {estado}.")
        return redirect(url_for("session_blueprint.ver_cliente", id=id))
    sesiones = Sesion.query.filter_by(idcliente=id).all()

    return render_template("asistenciaCliente.html", cliente=cliente, sesiones=sesiones)




def obtener_todos_los_clientes():
    return Clientes.query.all()


@cliente_blueprint.errorhandler(TypeError)
def handle_type_error(error):
    logging.exception("Error de tipo en la gestión de clientes: %s", error)
    flash("Se produjo un error de tipo, revisa los datos ingresados.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(AttributeError)
def handle_attribute_error(error):
    logging.exception("Error de atributo en la gestión de clientes: %s", error)
    flash("Se produjo un error al acceder a un atributo. Verifica los datos proporcionados.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(PermissionError)
def handle_permission_error(error):
    logging.exception("Error de permiso en la gestión de clientes: %s", error)
    flash("No tienes permiso para realizar esta acción.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(ValueError)
def handle_value_error(error):
    logging.exception("Error de valor en la gestión de clientes: %s", error)
    flash("Error en los datos ingresados. Por favor revisa los valores proporcionados.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    logging.exception("Error de integridad en la base de datos al gestionar clientes: %s", error)
    flash("Error al registrar o modificar datos. Verifica los valores ingresados.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(OperationalError)
def handle_operational_error(error):
    db.session.rollback()
    logging.exception("Error operativo de la base de datos al gestionar clientes: %s", error)
    flash("No se pudo conectar a la base de datos. Inténtalo más tarde.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(NoResultFound)
def handle_no_result_found(error):
    logging.exception("Cliente no encontrado: %s", error)
    flash("El cliente especificado no existe.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    db.session.rollback()
    logging.exception("Error general de SQLAlchemy al gestionar clientes: %s", error)
    flash("Se produjo un error al realizar la operación. Por favor, inténtalo más tarde.")
    return redirect("/clientes")

@cliente_blueprint.errorhandler(Exception)
def handle_generic_exception(error):
    logging.exception("Error genérico en la gestión de clientes: %s", error)
    flash("Ocurrió un error inesperado. Por favor, inténtalo más tarde.")
    return redirect("/clientes")