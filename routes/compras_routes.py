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

    compras = obtenerCompras()
    for compra in compras:
        id = compra['idcompra']
        total = db.session.execute(text('SELECT calcular_total_compra(:idC)'), {'idC': id}).scalar()
        compra['total'] = total if total is not None else 0

    datos_totales = obtener_totales_por_mes()
    meses = [fila[0] for fila in datos_totales] 
    totales = [fila[1] for fila in datos_totales] 

    img = BytesIO()
    crear_grafico(meses, totales, img)  
    img.seek(0) 
    graph_url = base64.b64encode(img.getvalue()).decode('utf-8') 

    return render_template("compras.html", compras=compras, graph_url=graph_url)

@compras_blueprint.route('/grafico', methods=['GET'])
def mostrar_grafico():
    return send_file('ganancias_mensuales.png', mimetype='image/png')

@compras_blueprint.route("/compras/agregar", methods=['GET', 'POST'])
def formCompra():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    if request.method == 'GET':
        empleados = obtener_todos_los_empleados()
        clientes = obtener_todos_los_clientes()
        productos = obtenerTodoslosProductos()
        return render_template("comprasForm.html", clientes=clientes, empleados=empleados, productos=productos)

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
            flash("No se pudo registrar la compra, stock insuficiente.")
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

@compras_blueprint.route('/compras/obtenerPrecioProducto/<int:product_id>', methods=['GET'])
def obtenerPrecioProducto(product_id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    producto = Productos.query.get(product_id)
    if producto:
        return jsonify({'precio': str(producto.preciov)})
    return jsonify({'precio': '0'}) 



@compras_blueprint.route("/compras/detallecompras/<int:id>", methods=['GET'])
def detallecompras(id):
    detalles = DetalleCompras.query.filter_by(idcompra=id).all()
    
    resultados = []
    for detalle in detalles:
        producto = Productos.query.get(detalle.idproducto)
        if producto:
            resultados.append({
                "producto": producto.nombre,
                "cantidad": detalle.cantidad,
                "subtotal": producto.preciov * detalle.cantidad
            })
    
    return jsonify({"resultados": resultados}) 




        


def obtener_totales_por_mes():
    resultados = db.session.execute(text("SELECT * FROM obtener_totales_por_mes();")).fetchall()
    return resultados



def crear_grafico(meses, totales, img):
    plt.figure(figsize=(10, 5))
    plt.bar(meses, totales, color='red')
    plt.xlabel('Meses')
    plt.gca().set_facecolor('#f6f6f6') 
    plt.ylabel('Total Ganancias')
    plt.title('Ganancias Mensuales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(img, format='png')
    plt.close()
