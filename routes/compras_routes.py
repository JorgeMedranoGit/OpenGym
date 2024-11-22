from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify, send_file
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
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

from io import BytesIO
import base64


compras_blueprint = Blueprint('compras_blueprint', __name__)



@compras_blueprint.route("/compras", methods=['GET', 'POST'])
def compraCrud():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    compras = []
    
    if session["rol"] == "Administrador":
        # Si el usuario es Administrador, obtenemos todas las compras
        compras = obtenerCompras()
        for compra in compras:
            id = compra['idcompra']
            total = db.session.execute(text('SELECT calcular_total_compra(:idC)'), {'idC': id}).scalar()
            compra['total'] = total if total is not None else 0
    elif session["rol"] == "Recepcionista":
        compras = obtenerCompras_emp()
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

    # Envío de la lista al HTML de compras
    return render_template("compras.html", 
                           compras=compras, 
                           total_compras=total_compras, 
                           total_compras_individual=total_compras_individual, 
                           rol=session["rol"],
                           producto_mas_comprado=producto_mas_comprado,
                           )


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
        try:
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
        except:
            flash("No se pudo registrar la compra, intentelo mas tarde")
            return redirect("/compras")

def obtenerCompras():
    compras = Compras.query.all()
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

