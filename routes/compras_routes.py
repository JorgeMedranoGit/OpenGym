from flask import Blueprint, Flask, json, redirect, url_for, render_template, request, session, flash, jsonify, send_file
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError, NoResultFound
from models.compras import Compras
from models.detalleCompra import DetalleCompras
from models.productos import Productos
from database import db
from sqlalchemy import text
from routes.empleados_routes import obtener_todos_los_empleados
from routes.clientes_routes import obtener_todos_los_clientes
from routes.productos_routes import obtenerTodoslosProductos
import matplotlib
from datetime import datetime
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import logging

from io import BytesIO
import base64


compras_blueprint = Blueprint('compras_blueprint', __name__)

@compras_blueprint.route("/compras", methods=['GET', 'POST'])
def compraCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    compras = []
    session['thead'] = None
    session['tbody'] = None
    session['extra'] = None
    # Obtener todos los empleados y clientes disponibles para el filtro, tambien las fechas
    empleados = db.session.execute(text('SELECT idempleado, nombre FROM empleados')).fetchall()
    clientes = db.session.execute(text('SELECT idcliente, nombre FROM clientes')).fetchall()
    fecha_inicio = request.form.get('fecha_inicio')
    fecha_fin = request.form.get('fecha_fin')
    
    # Convertir las fechas si están presentes
    if fecha_inicio:
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    # Filtros seleccionados
    empleado_id = request.form.get('empleado_id')
    cliente_id = request.form.get('cliente_id')

    # Filtrar las compras según el rol y los filtros seleccionados
    if session["rol"] == "Administrador":
        compras = obtenerCompras(empleado_id, cliente_id, fecha_inicio, fecha_fin)
    elif session["rol"] == "Recepcionista":
        compras = obtenerCompras_emp(empleado_id, cliente_id)

    for compra in compras:
        id = compra['idcompra']
        total = db.session.execute(text('SELECT calcular_total_compra(:idC)'), {'idC': id}).scalar()
        compra['total'] = total if total is not None else 0

    # Obtención de totales para el Administrador
    total_compras = db.session.execute(text('SELECT calcular_total_compras_admin()')).scalar()
    total_compras_individual = db.session.execute(text('SELECT calcular_total_compras_individual(:idemp)'), {'idemp': session["empleado_id"]}).scalar()
    
    # Obtener el producto con más compras
    producto_mas_comprado = db.session.execute(text(''' 
        SELECT p.idp, p.nombre, SUM(c.cantidad) AS total_compras 
        FROM detallecompras c 
        JOIN productos p ON c.idproducto = p.idp 
        GROUP BY p.idp, p.nombre 
        ORDER BY total_compras DESC 
        LIMIT 1; 
    ''')).fetchone()

    claves = list(compras[0].keys()) if compras else []
    valores = [list(compra.values()) for compra in compras]

    thead = []
    tbody = []

    # Recorre los elementos directamente, sin usar índices
    for clave in claves:
        thead.append("<th>" + clave + "</th>")

    for fila in valores:
        fila_html = "<tr>"
        for valor in fila:
            fila_html += f"<td>{valor}</td>"
        fila_html += "</tr>"
        tbody.append(fila_html)

    thead_html = "<tr>" + "".join(thead) + "</tr>"
    tbody_html = "".join(tbody)

    suma_total = 0.0

    for fila in valores:
        total_str = fila[-1]
        total_float = float(total_str)
        suma_total += total_float

    print("Suma total:", suma_total)

    suma_total = "<tr><td></td><td></td><td></td><td></td><td></td><td></td><td>" + str(suma_total) + "</td></tr>"

    session['thead'] = thead_html
    session['tbody'] = tbody_html
    session['extra'] = suma_total


    return render_template("compras.html", 
                           compras=compras, 
                           total_compras=total_compras, 
                           total_compras_individual=total_compras_individual, 
                           rol=session["rol"],
                           producto_mas_comprado=producto_mas_comprado,
                           empleados=empleados,
                           clientes=clientes,
                           empleado_id=empleado_id,
                           cliente_id=cliente_id,
                           resultado=json.dumps(compras))



# Ruta para agregar una compra
@compras_blueprint.route("/compras/agregar", methods=['GET', 'POST'])
def formCompra():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    if session["rol"] == "Administrador" or session["rol"] == "Recepcionista":
        if request.method == 'GET':
            empleados = obtener_todos_los_empleados()
            clientes = obtener_todos_los_clientes()
            productos = obtenerTodoslosProductos()
            return render_template("comprasForm.html", clientes=clientes, empleados=empleados, productos=productos, rol = session["rol"])

    if request.method == 'POST':
        
        fechacompra = request.form['fechacompra']
        metodopago = request.form['metodopago']
        idempleado = request.form['idempleado']
        idcliente = request.form['idcliente']

        productos = request.form.getlist('producto[]')
        cantidades = request.form.getlist('cantidad[]')

        # Convertir fechacompra a objeto datetime
        fecha_compra_dt = datetime.strptime(fechacompra, '%Y-%m-%dT%H:%M')

        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Comparar fechas
        if fecha_compra_dt > fecha_actual:
            flash("La fecha de compra no puede ser mayor a la fecha actual.")
            return redirect("/compras")
    
    # Aquí puedes continuar con el procesamiento si la fecha es válida

        if not cantidades or not productos:
            flash("Datos ingresados incorrectamente")
            return redirect("/compras")

        stock_ok = True
        for producto, cantidad in zip(productos, cantidades):
            if producto.strip() and int(cantidad) > 0:
                producto_db = Productos.query.get(producto) 
                if producto_db and producto_db.stock < int(cantidad):
                    stock_ok = False
                    break
        
        if not stock_ok:
            flash("No se pudo registrar la compra, stock insuficientes.")
            return redirect("/compras")

        compraN = Compras(fechacompra=fechacompra, metodopago=metodopago, idcliente=idcliente, idempleado=idempleado)
        db.session.add(compraN) 
        db.session.commit()

        idCompra = compraN.idcompra 

        for producto, cantidad in zip(productos, cantidades):
            if producto.strip() and int(cantidad) > 0:
                detalle = DetalleCompras(cantidad=int(cantidad), idcompra=idCompra, idproducto=producto)
                db.session.add(detalle)

                # Restar del stock
                producto_db = Productos.query.get(producto)
                if producto_db:
                    producto_db.stock -= int(cantidad)

        db.session.commit()
        flash("Compra agregada exitosamente!")
        return redirect("/compras")    


def obtenerCompras(empleado_id=None, cliente_id=None, fecha_inicio=None, fecha_fin=None):
    # Comenzamos con una consulta base que obtiene todas las compras
    query = Compras.query
    print(f"Empleado seleccionado: {empleado_id}")

    # Filtramos por empleado_id si se proporciona
    if empleado_id:
        query = query.filter(Compras.idempleado == empleado_id)  # Asegúrate de filtrar por la columna idempleado

    # Filtramos por cliente_id si se proporciona
    if cliente_id:
        query = query.filter(Compras.idcliente == cliente_id)

    # Filtrar por fecha de inicio si se proporciona
    if fecha_inicio:
        query = query.filter(Compras.fechacompra >= fecha_inicio)

    # Filtrar por fecha de fin si se proporciona
    if fecha_fin:
        query = query.filter(Compras.fechacompra <= fecha_fin)

    # Ejecutamos la consulta
    compras = query.all()
    resultado = []
    
    # Formateamos los resultados
    for compra in compras:
        fecha_formateada = compra.fechacompra.strftime("%d/%m/%Y")
        hora_formateada = compra.fechacompra.strftime("%H:%M:%S")
        resultado.append({
            'idcompra': compra.idcompra,
            'nombreempleado': compra.empleado.nombre,  # Aquí puedes acceder al nombre del empleado a través de la relación
            'nombrecliente': compra.cliente.nombre,
            'fechacompra': fecha_formateada,
            'horacompra': hora_formateada,
            'metodopago': compra.metodopago
        })
    return resultado


def obtenerCompras_emp():
    compras = Compras.query.filter_by(idempleado= session["empleado_id"])
    resultado = []
    
    for compra in compras:
        fecha_formateada = compra.fechacompra.strftime("%d/%m/%Y")
        hora_formateada = compra.fechacompra.strftime("%H:%M:%S")
        resultado.append({
            'idcompra': compra.idcompra,
            'nombreempleado': compra.empleado.nombre,
            'nombrecliente': compra.cliente.nombre,
            'fechacompra': fecha_formateada,
            'horacompra': hora_formateada,
            'metodopago': compra.metodopago
        })
    return resultado

@compras_blueprint.route('/compras/obtenerPrecioProducto/<int:product_id>', methods=['GET'])
def obtenerPrecioProducto(product_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    producto = Productos.query.get(product_id)
    if producto:
        return jsonify({'precio': str(producto.preciov)})
    return jsonify({'precio': '0'}) 



# Ruta para obtener los productos en cada compra


# Función para obtener el precio histórico
def obtener_precio_historico(id_producto, fecha_compra):
    precio_historico = db.session.execute(
        text('''
            SELECT precioventa
            FROM historialprecios
            WHERE idp = :id_producto AND fecha <= :fecha_compra
            ORDER BY fecha DESC
            LIMIT 1
        '''),
        {'id_producto': id_producto, 'fecha_compra': fecha_compra}
    ).fetchone()
    
    if precio_historico:
        return precio_historico[0]  # Devuelve el precio histórico encontrado
    return 0  # Precio predeterminado si no se encuentra en el historial


@compras_blueprint.route("/compras/detallecompras/<int:id>", methods=['GET'])
def detallecompras(id):
    detalles = DetalleCompras.query.filter_by(idcompra=id).all()
    compra = Compras.query.get(id)  # Obtener la fecha de la compra
    
    if not compra:
        return jsonify({"error": "Compra no encontrada"}), 404
    
    resultados = []
    for detalle in detalles:
        producto = Productos.query.get(detalle.idproducto)
        if producto:
            # Obtener el precio histórico vigente en la fecha de compra
            precio_historico = obtener_precio_historico(detalle.idproducto, compra.fechacompra)
            subtotal = precio_historico * detalle.cantidad  # Calcular el subtotal correcto
            
            resultados.append({
                "producto": producto.nombre,
                "cantidad": detalle.cantidad,
                "subtotal": subtotal
            })
    
    return jsonify({"resultados": resultados})










# Logging
@compras_blueprint.errorhandler(TypeError)
def handle_type_error(error):
    logging.exception("Error de tipo: %s", error)
    flash("Se produjo un error de tipo, revisa los datos ingresados.")
    return redirect("/compras")

@compras_blueprint.errorhandler(AttributeError)
def handle_attribute_error(error):
    logging.exception("Error de atributo: %s", error)
    flash("Se produjo un error al acceder a un atributo, por favor verifica los datos.")
    return redirect("/compras")

@compras_blueprint.errorhandler(PermissionError)
def handle_permission_error(error):
    logging.exception("Error de permiso: %s", error)
    flash("No tienes permiso para realizar esta acción.")
    return redirect("/compras")

@compras_blueprint.errorhandler(ValueError)
def handle_integrity_error(error):
    db.session.rollback()
    logging.exception("Error de conversión de datos: %s", error)
    flash("Error de datos ingresados, revisa los valores y vuelve a intentarlo.")
    return redirect("/compras")

@compras_blueprint.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    logging.exception("Error de integridad en la base de datos: %s", error)
    flash("Error al registrar la compra, datos de integridad inválidos.")
    return redirect("/compras")

@compras_blueprint.errorhandler(OperationalError)
def handle_operational_error(error):
    db.session.rollback()
    logging.exception("Error de conexión a la base de datos: %s", error)
    flash("No se pudo conectar a la base de datos, por favor intenta más tarde.")
    return redirect("/compras")

@compras_blueprint.errorhandler(NoResultFound)
def handle_no_result_found(error):
    db.session.rollback()
    logging.exception("Producto o empleado no encontrado: %s", error)
    flash("El producto o empleado especificado no existe.")
    return redirect("/compras")

@compras_blueprint.errorhandler(SQLAlchemyError)
def handle_sqlalchemy_error(error):
    db.session.rollback()
    logging.exception("Error general de SQLAlchemy: %s", error)
    flash("Se produjo un error al registrar la compra, por favor intenta más tarde.")
    return redirect("/compras")

@compras_blueprint.errorhandler(Exception)
def handle_generic_exception(error):
    logging.exception("Otro error del servidor: %s", error)
    flash("No se pudo registrar la compra, intentelo más tarde.")
    return redirect("/compras")



