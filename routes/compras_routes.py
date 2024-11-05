from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify
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

compras_blueprint = Blueprint('compras_blueprint', __name__)

@compras_blueprint.route("/compras" , methods=['GET', 'POST'])
def compraCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    compras = obtenerCompras()
    for compra in compras:
        id = compra['idcompra']
        total = db.session.execute(text('SELECT calcular_total_compra(:idC)'), {'idC': id}).scalar()
        compra['total'] = total if total is not None else 0
    return render_template("compras.html", compras=compras)

@compras_blueprint.route("/compras/agregar", methods=['GET', 'POST'])
def formCompra():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if request.method == 'GET':
        empleados = obtener_todos_los_empleados()
        clientes = obtener_todos_los_clientes()
        return render_template("comprasForm.html", clientes = clientes, empleados = empleados)
    if request.method == 'POST':
        fechacompra = request.form['fechacompra']
        metodopago = request.form['metodopago']
        idempleado = request.form['idempleado']
        idcliente = request.form['idcliente']

        compraN = Compras(fechacompra=fechacompra, metodopago=metodopago,idcliente=idcliente, idempleado=idempleado)
        db.session.add(compraN)  # Añadir la compra a la sesión antes de hacer commit
        db.session.commit()  # Insertar la compra y obtener el id

        idCompra = compraN.idcompra  # Obtener el id después de hacer commit

        productos = request.form.getlist('producto[]')  # Cambiar a getlist
        cantidades = request.form.getlist('cantidad[]')  # Cambiar a getlist

        for producto, cantidad in zip(productos, cantidades):
            if producto.strip() and int(cantidad) > 0:
                detalle = DetalleCompras(cantidad=int(cantidad), idcompra=idCompra, idproducto=producto)
                db.session.add(detalle)

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
        return jsonify({'precio': str(producto.preciov)})  # Asegúrate de convertir a string si es necesario
    return jsonify({'precio': '0'})  # Retorna 0 como string
