from flask import Blueprint, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, date
from decimal import Decimal
from models.clientes import Clientes
from models.detalleMembresia import DetalleMembresia
from models.membresias import Membresias
from models.pagos import Pago
from database import db

cliente_blueprint = Blueprint('cliente_blueprint', __name__)

@cliente_blueprint.route("/clientes", methods=["POST", "GET"])
def clientesCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))
    
    # termino_busqueda = request.args.get("buscar", "").strip()

    if request.method == "POST":
    # Obtener datos del formulario
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        carnet = request.form['carnet']
        telefono = request.form['telefono']
        tipo_suscripcion = request.form['tipo_suscripcion']
        cliente_id = request.form.get('cliente_id')  # Si es edición, este campo vendrá con el ID del cliente

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

            # Manejo de suscripción si el cliente es nuevo
            if tipo_suscripcion == "membresia":
                membresia_id = request.form.get("membresia_id")
                metodo_pago = request.form.get("metodo_pago")

                membresia_info = Membresias.query.filter_by(idmembresia=membresia_id, habilitado=True).first()
                if membresia_info:  # Verifica que exista y esté habilitada
                    # Crear nueva membresía para el cliente
                    nueva_membresia = DetalleMembresia(
                        idcliente=nuevo_cliente.idcliente,
                        idmembresia=membresia_id,
                        fechainicio=date.today(),
                        fechavencimiento=date.today() + timedelta(days=30)
                    )
                    db.session.add(nueva_membresia)
                    
                    # Crear pago para la membresía
                    monto = membresia_info.costo
                    nuevo_pago = Pago(
                        idcliente=nuevo_cliente.idcliente,
                        idmembresia=membresia_id,
                        monto=monto,
                        metodopago=metodo_pago,
                        estado="pagado" if metodo_pago else "pendiente"
                    )
                    db.session.add(nuevo_pago)
                else:
                    flash("La membresía seleccionada no está activa.")

            elif tipo_suscripcion == "sesion":
                # Crear pago de sesión individual
                metodo_pago = request.form.get("metodo_pago", "efectivo")
                monto = Decimal("20.00")  # Monto fijo para una sesión

                nuevo_pago = Pago(
                    idcliente=nuevo_cliente.idcliente,
                    idmembresia=None,  # No hay membresía en este caso
                    monto=monto,
                    metodopago=metodo_pago,
                    estado="pagado" if metodo_pago else "pendiente"
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
    ).filter(Clientes.activo == True).all()


    # Consulta de clientes inactivos
    clientes_inactivos = Clientes.query.filter_by(activo=False).all()

    # Consulta de todas las membresías
    membresias = Membresias.query.filter_by(habilitado=True).all()


    return render_template(
        "clientes.html", 
        clientes=clientes, 
        clientes_inactivos=clientes_inactivos, 
        membresias=membresias
    )

    

# Ruta para editar cliente
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
            membresias=membresias
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


@cliente_blueprint.route("/clientes/activar/<int:id>", methods=["POST"])
def activarCliente(id):
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))

    cliente = Clientes.query.get(id)
    if cliente:
        cliente.activo = True
        db.session.commit()
        flash("Cliente reactivado exitosamente!")
    return redirect(url_for("cliente_blueprint.clientesCrud"))


# Función para obtener todos los clientes (helper function)
def obtener_todos_los_clientes():
    return Clientes.query.all()