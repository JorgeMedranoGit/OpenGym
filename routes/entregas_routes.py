from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file
from datetime import timedelta, datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.entregas import Entregas
from models.detalleEntregas import DetalleEntregas
from models.productos import Productos
from models.estados import Estados
from models.proveedores import Proveedores
from models.entregaestado import EntregaEstado
from database import db
from sqlalchemy import text
from routes.proveedores_routes import obtenerTodoslosProveedores
from routes.productos_routes import obtenerTodoslosProductos
from routes.estados_routes import obtener_todos_los_estados


entregas_blueprint = Blueprint('entregas_blueprint', __name__)


# Ruta para listar las entregas

@entregas_blueprint.route("/entregas" , methods=['GET', 'POST'])
def entregaCrud():
    # Verificacion de inicio de sesion 
    if "email" not in session:
       flash("Debes iniciar sesión")
       return redirect("/login")
    
    # Obtencion de entregas y estados, para listarlos y permitir el cambio de estado en un combobox
    entregas = obtenerEntregas()
    estados = obtener_todos_los_estados()

    # Funcion para  calcular los totales y extraer los estados de cada entrega, luego agregarlos a una lista
    for entrega in entregas:
        id = entrega['identrega']
        total = db.session.execute(text('SELECT calcular_total_entrega(:idC)'), {'idC': id}).scalar()
        estado = db.session.execute(text('SELECT devolver_ultimo_estado(:idC)'),{'idC': id}).scalar()
        entrega['total'] = total if total is not None else 0
        entrega['estado'] = estado if estado is not None else "Pendiente"
        entrega['fechaestado'] = db.session.execute(
            text('SELECT es.fechaestado FROM entregaestado es WHERE identrega = :identrega ORDER BY idestado DESC'),
            {'identrega': id} 
        ).scalar()
        if entrega['fechaestado'] is not None:
            entrega['fechaestado'] = entrega['fechaestado'].strftime("%d/%m/%Y")
        else:
        # Manejo cuando fechaestado es None, asignar un valor por defecto si es necesario
            entrega['fechaestado'] = "Fecha no disponible"
    # Envio de las listas creadas previamente
    return render_template("entregas.html", entregas=entregas, estados = estados)


# Ruta para agregar entregas
@entregas_blueprint.route("/entregas/agregar", methods=['GET', 'POST'])
def formEntrega():
    # Verificacion de la sesion
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    # Cargar el formulario enviando los proveedores y productos para los comboboxes
    if request.method == 'GET':
        proveedores = obtenerTodoslosProveedores()
        productos = obtenerTodoslosProductos()
        return render_template("entregasForm.html", proveedores=proveedores, productos=productos)

    # Accion POST
    if request.method == 'POST':
        try: 
            # Obtencion de los inputs, [] se usa para las listas
            fechapedido = request.form['fechapedido']
            metodopago = request.form['metodopago']
            idproveedor = request.form['idproveedor']
            cantidades = request.form.getlist('cantidad[]')
            preciosCompras = request.form.getlist('precio[]') 

            fechapedido_dt = datetime.strptime(fechapedido, '%Y-%m-%dT%H:%M')

            # Obtener la fecha actual
            fecha_actual = datetime.now()

            # Comparar fechas
            if fechapedido_dt > fecha_actual:
                flash("La fecha de compra no puede ser mayor a la fecha actual.")
                return redirect("/entregas")

            # Validacion de formulario
            if not cantidades or not preciosCompras:
                flash("Datos ingresados incorrectamente")
                return redirect("/entregas")
            
            # Insercion de la entrega
            entregaN = Entregas(fechapedido=fechapedido, metodopago=metodopago, idproveedor=idproveedor)
            db.session.add(entregaN) 
            db.session.commit() 

            # Insercion del estado, inicializado como pendiente (idestado = 1)
            idEntrega = entregaN.identrega

            estadoN = EntregaEstado(fechaestado=datetime.now(), identrega=idEntrega, idestado=1)
            db.session.add(estadoN)
            db.session.commit()

            
            # Insercion del detalle iterando sobre idp
            productos = request.form.getlist('idp[]')
            for idp, cantidad, precio in zip(productos, cantidades, preciosCompras):
                if idp.strip() and int(cantidad) > 0 and float(precio) > 0:
                    detalle = DetalleEntregas(cantidad=int(cantidad), preciocompra=float(precio), identrega=idEntrega, idproducto=idp)
                    db.session.add(detalle)

                    producto_db = Productos.query.get(idp)
                    if producto_db:
                        producto_db.stock += int(cantidad)
            db.session.commit()
            flash("Entrega agregada exitosamente!")
            return redirect("/entregas")
        
        # Excepcion
        except:
            flash("No se pudo registrar la entrega ahora, intentelo mas tarde")
            return redirect("/entregas")

@entregas_blueprint.route("/entregas/detalleentrega/<int:id>", methods=['GET'])
def detallecompras(id):
    detalles = DetalleEntregas.query.filter_by(identrega=id).all()
    
    resultados = []
    for detalle in detalles:
        producto = Productos.query.get(detalle.idp)
        if producto:
            resultados.append({
                "producto": producto.nombre,
                "cantidad": detalle.cantidad,
                "subtotal": producto.preciov * detalle.preciocompra
            })
    
    return jsonify({"resultados": resultados}) 


@entregas_blueprint.route("/entregas/cambiar_estado", methods=['POST'])
def cambiar_estado():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    entrega_id = request.form.get("entrega_id")
    estado_id = request.form.get("estado_id")
    
    if entrega_id and estado_id:
        fecha_actual = datetime.now()
        
        db.session.execute(
            text('INSERT INTO entregaestado (fechaestado, identrega, idestado) VALUES (:fecha, :entrega_id, :estado_id)'),
            {'fecha': fecha_actual, 'entrega_id': entrega_id, 'estado_id': estado_id}
        )
        
        if estado_id == '2':
            precio_compra_result = db.session.execute(
                text('SELECT preciocompra, idp FROM detalleentregas WHERE identrega = :entrega_id LIMIT 1'),
                {'entrega_id': entrega_id}
            ).fetchone()
            
            if precio_compra_result:
                v_preciocompra = precio_compra_result[0]
                producto_id = precio_compra_result[1]

                nuevo_precio_venta = v_preciocompra + (v_preciocompra * Decimal(0.30))

                precio_venta_actual_result = db.session.execute(
                    text('SELECT preciov FROM productos WHERE idp = :producto_id'),
                    {'producto_id': producto_id}
                ).fetchone()

                if precio_venta_actual_result:
                    v_precioventa_actual = precio_venta_actual_result[0]

                    if v_precioventa_actual != nuevo_precio_venta:
                        db.session.execute(
                            text('UPDATE productos SET preciov = :nuevo_precio WHERE idp = :producto_id'),
                            {'nuevo_precio': nuevo_precio_venta, 'producto_id': producto_id}
                        )

                        db.session.execute(
                            text('INSERT INTO historialprecios (precioventa, fecha, idp) VALUES (:nuevo_precio, :fecha_actual, :producto_id)'),
                            {'nuevo_precio': nuevo_precio_venta, 'fecha_actual': fecha_actual, 'producto_id': producto_id}
                        )

        db.session.commit()
        flash("Estado de la entrega actualizado exitosamente", "success")
    else:
        flash("No se pudo actualizar el estado de la entrega. Entrega: " + str(entrega_id) + " Estado: " + str(estado_id), "danger")

    return redirect(url_for("entregas_blueprint.entregaCrud"))



def obtenerEntregas():
    entregas = Entregas.query.order_by(Entregas.identrega.desc()).all()

    resultado = []
    
    for entrega in entregas:
        fecha_formateada = entrega.fechapedido.strftime("%d/%m/%Y")
        hora_formateada = entrega.fechapedido.strftime("%H:%M:%S")
        resultado.append({
            'identrega': entrega.identrega,
            'fechaentrega': fecha_formateada,
            'horaentrega': hora_formateada,
            'metodopago': entrega.metodopago,
            "proveedor": entrega.proveedor.nombre
        })
    return resultado

