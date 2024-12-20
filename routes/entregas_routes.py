from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file
from datetime import timedelta, datetime
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.entregas import Entregas
from models.detalleEntregas import DetalleEntregas
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError, NoResultFound
from models.productos import Productos
from models.estados import Estados
from models.proveedores import Proveedores
from models.entregaestado import EntregaEstado
from models.historialprecio import HistorialPrecios
from database import db
from sqlalchemy import text
from routes.proveedores_routes import obtenerTodoslosProveedores
from routes.productos_routes import obtenerTodoslosProductos
from routes.estados_routes import obtener_todos_los_estados

import logging


entregas_blueprint = Blueprint('entregas_blueprint', __name__)


# Ruta para listar las entregas

@entregas_blueprint.route("/entregas", methods=['GET', 'POST'])
def entregaCrud():
    # Verificación de inicio de sesión
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    if session["rol"] == "Administrador":
        session['thead'] = None
        session['tbody'] = None
        session['extra'] = None
        # Obtención de entregas y estados, para listarlos y permitir el cambio de estado en un combobox
        proveedor_id = request.form.get('proveedor_id')
        print(f"Proveedor seleccionado: {proveedor_id}")  # Debugging

        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        # Obtener entregas aplicando filtros
        entregas = obtenerEntregas(proveedor_id, fecha_inicio, fecha_fin)

        # Obtener proveedores para el filtro en la plantilla
        proveedores = db.session.execute(text('SELECT idproveedor, nombre FROM proveedores')).fetchall()
        estados = obtener_todos_los_estados()
        claves = list(entregas[0].keys()) if entregas else []
        valores = [list(entrega.values()) for entrega in entregas]

        thead = []
        tbody = []

        # Construir la cabecera de la tabla
        for clave in claves:
            thead.append(f"<th>{clave}</th>")
        
        # Construir el cuerpo de la tabla
        for fila in valores:
            fila_html = "<tr>"
            for valor in fila:
                fila_html += f"<td>{valor}</td>"
            fila_html += "</tr>"
            tbody.append(fila_html)

        # Guardar HTML en la sesión
        session['thead'] = "<tr>" + "".join(thead) + "</tr>"
        session['tbody'] = "".join(tbody)
        session['extra']=''
        # Inicialización de variables para calcular los totales
        proveedor_mas_solicitado = None
        producto_mas_solicitado = None
        total_gastado = 0

        # Diccionarios para contar productos y proveedores
        proveedor_contador = {}
        producto_contador = {}

        # Función para calcular los totales y extraer los estados de cada entrega
        for entrega in entregas:
            id = entrega['identrega']  # Cambiado de 'entrega['identrega']' a 'entrega.identrega'
            
            # Calcular el total de la entrega
            total = db.session.execute(text('SELECT calcular_total_entrega(:idC)'), {'idC': id}).scalar()
            total_gastado += total if total else 0

            proveedor_id = entrega['idproveedor'] 
            if proveedor_id in proveedor_contador:
                proveedor_contador[proveedor_id] += 1
            else:
                proveedor_contador[proveedor_id] = 1

            detalle_entrega = db.session.execute(
                text('SELECT * FROM detalleentregas WHERE identrega = :identrega'), {'identrega': id}
            ).fetchall()

            # Calcular el producto más solicitado
            for detalle in detalle_entrega:
                producto_id = detalle[1] 
                cantidad = detalle[0] 
                
                if producto_id in producto_contador:
                    producto_contador[producto_id] += cantidad
                else:
                    producto_contador[producto_id] = cantidad

            estado = db.session.execute(text('SELECT devolver_ultimo_estado(:idC)'), {'idC': id}).scalar()
            entrega['estado'] = estado if estado else "Pendiente"
            entrega['fechaestado'] = db.session.execute(
                text('SELECT es.fechaestado FROM entregaestado es WHERE identrega = :identrega ORDER BY idestado DESC'),
                {'identrega': id}
            ).scalar()
            if entrega['fechaestado']:
                entrega['fechaestado'] = entrega['fechaestado'].strftime("%d/%m/%Y")
            else:
                entrega['fechaestado'] = "Fecha no disponible"

        proveedor = "N/A"

        if proveedor_contador:
            proveedor_mas_solicitado = max(proveedor_contador, key=proveedor_contador.get)
            proveedor_obj = Proveedores.query.get(proveedor_mas_solicitado)
            if proveedor_obj:
                proveedor = proveedor_obj.nombre

        if producto_contador:
            producto_mas_solicitado = db.session.execute(
                text('''
                    SELECT p.nombre, SUM(de.cantidad) AS total
                    FROM detalleentregas de
                    JOIN productos p ON de.idp = p.idp
                    GROUP BY p.idp, p.nombre
                    ORDER BY total DESC
                    LIMIT 1
                ''')
            ).fetchone()

            if producto_mas_solicitado:
                p_nom = producto_mas_solicitado[0]  
                p_total = producto_mas_solicitado[1]

                producto_mas_solicitado_dict = {'nombre': p_nom, 'total': p_total}
            else:
                producto_mas_solicitado_dict = {'nombre': 'N/A', 'total': 0}
        else:
            producto_mas_solicitado_dict = {'nombre': 'N/A', 'total': 0}

        return render_template("entregas.html", entregas=entregas, estados=estados, 
                               proveedor_mas_solicitado=proveedor, 
                               producto_mas_solicitado=producto_mas_solicitado_dict,
                               proveedores = proveedores,
                               total_gastado=total_gastado, rol=session["rol"])
    else:
        flash("No tienes permisos suficientes")
        return redirect("tareasCom")



# Ruta para agregar entregas
@entregas_blueprint.route("/entregas/agregar", methods=['GET', 'POST'])
def formEntrega():
    # Verificacion de la sesion
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session["rol"] == "Administrador":
        # Cargar el formulario enviando los proveedores y productos para los comboboxes
        if request.method == 'GET':
            proveedores = obtenerTodoslosProveedores()
            productos = obtenerTodoslosProductos()
            return render_template("entregasForm.html", proveedores=proveedores, productos=productos, rol = session["rol"])

        # Accion POST
        if request.method == 'POST':
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
            
        else:
            flash("No tienes permisos suficientes")
            return redirect("tareasCom")
    else:
        flash("No tienes permisos suficientes")
        return redirect("/tareasCom")  


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
                "subtotal": detalle.cantidad * detalle.preciocompra  # Cálculo correcto
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
            # Obtener todos los productos de la entrega
            productos_result = db.session.execute(
                text('SELECT preciocompra, idp FROM detalleentregas WHERE identrega = :entrega_id'),
                {'entrega_id': entrega_id}
            ).fetchall()
            
            for producto in productos_result:
                v_preciocompra = producto[0]
                producto_id = producto[1]

                # Calcular nuevo precio de venta
                nuevo_precio_venta = v_preciocompra + (v_preciocompra * Decimal(0.30))

                # Obtener precio de venta actual
                precio_venta_actual_result = db.session.execute(
                    text('SELECT preciov FROM productos WHERE idp = :producto_id'),
                    {'producto_id': producto_id}
                ).fetchone()

                if precio_venta_actual_result:
                    v_precioventa_actual = precio_venta_actual_result[0]

                    if v_precioventa_actual != nuevo_precio_venta:
                        # Actualizar precio de venta en productos
                        db.session.execute(
                            text('UPDATE productos SET preciov = :nuevo_precio WHERE idp = :producto_id'),
                            {'nuevo_precio': nuevo_precio_venta, 'producto_id': producto_id}
                        )

                        # Insertar en historial de precios
                        db.session.execute(
                            text('INSERT INTO historialprecios (precioventa, fecha, idp) VALUES (:nuevo_precio, :fecha_actual, :producto_id)'),
                            {'nuevo_precio': nuevo_precio_venta, 'fecha_actual': fecha_actual, 'producto_id': producto_id}
                        )

        db.session.commit()
        flash("Estado de la entrega actualizado exitosamente", "success")
    else:
        flash(f"No se pudo actualizar el estado de la entrega. Entrega: {entrega_id} Estado: {estado_id}", "danger")

    return redirect(url_for("entregas_blueprint.entregaCrud"))




def obtenerEntregas(proveedor_id=None, fecha_inicio=None, fecha_fin=None):
    # Consulta base para obtener entregas
    query = Entregas.query
    
    if proveedor_id:
        query = query.filter(Entregas.idproveedor == proveedor_id)
    
    if fecha_inicio:
        query = query.filter(Entregas.fechapedido >= fecha_inicio)
    
    if fecha_fin:
        query = query.filter(Entregas.fechapedido <= fecha_fin)

    # Obtener entregas ordenadas
    entregas = query.order_by(Entregas.identrega.desc()).all()

    resultado = []
    for entrega in entregas:
        # Obtener detalles de la entrega
        detalles = DetalleEntregas.query.filter_by(identrega=entrega.identrega).all()
        
        # Calcular el subtotal de la entrega
        subtotal_entrega = sum(detalle.cantidad * detalle.preciocompra for detalle in detalles)
        print(subtotal_entrega)
        # Formatear fecha y hora
        fecha_formateada = entrega.fechapedido.strftime("%d/%m/%Y")
        hora_formateada = entrega.fechapedido.strftime("%H:%M:%S")
        
        # Añadir datos al resultado
        resultado.append({
            'identrega': entrega.identrega,
            'fechaentrega': fecha_formateada,
            'horaentrega': hora_formateada,
            'metodopago': entrega.metodopago,
            'proveedor': entrega.proveedor.nombre,
            'idproveedor': entrega.proveedor._id,  # Asegúrate de que la columna sea correcta
            'subtotal': subtotal_entrega  # Agregar el subtotal calculado
        })
    return resultado









@entregas_blueprint.errorhandler(TypeError)
def handle_type_error(error):
    logging.exception("Error de tipo: %s", error)
    flash("Se produjo un error de tipo, revisa los datos ingresados.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(AttributeError)
def handle_attribute_error(error):
    logging.exception("Error de atributo: %s", error)
    flash("Se produjo un error al acceder a un atributo, por favor verifica los datos.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(PermissionError)
def handle_permission_error(error):
    logging.exception("Error de permiso: %s", error)
    flash("No tienes permiso para realizar esta acción.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(ValueError)
def handle_value_error(error):
    db.session.rollback()
    logging.exception("Error de conversión de datos: %s", error)
    flash("Error de datos ingresados, revisa los valores y vuelve a intentarlo.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    logging.exception("Error de integridad en la base de datos: %s", error)
    flash("Error al registrar la entrega, datos de integridad inválidos.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(OperationalError)
def handle_operational_error(error):
    db.session.rollback()
    logging.exception("Error de conexión a la base de datos: %s", error)
    flash("No se pudo conectar a la base de datos, por favor intenta más tarde.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(NoResultFound)
def handle_no_result_found(error):
    db.session.rollback()
    logging.exception("Producto o empleado no encontrado: %s", error)
    flash("El producto o empleado especificado no existe.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    db.session.rollback()
    logging.exception("Error general de SQLAlchemy: %s", error)
    flash("Se produjo un error al registrar la entrega, por favor intenta más tarde.")
    return redirect("/entregas")

@entregas_blueprint.errorhandler(Exception)
def handle_generic_exception(error):
    logging.exception("Otro error del servidor: %s", error)
    flash("No se pudo registrar la entrega, intentelo más tarde.")
    return redirect("/entregas")
