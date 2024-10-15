from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.productos import Productos
from database import db


productos_blueprint = Blueprint('productos_blueprint', __name__)

@productos_blueprint.route("/productos", methods=["POST", "GET"])
def productosCrud():
    if request.method == "POST":
        nombre = request.form['nombreProduc']
        precioVenta = Decimal(request.form['precioProduc'])  
        stock = int(request.form['stockProduc']) 
        
        producto_id = request.form.get('producto_id')  
        if producto_id: 
            producto = Productos.query.get(producto_id)
            producto.nombre = nombre
            producto.preciov = precioVenta
            producto.stock = stock
            db.session.commit() 
            flash("Producto editado exitosamente!")
        else:
            nuevo_producto = Productos(nombre, precioVenta, stock)
            db.session.add(nuevo_producto)
            db.session.commit() 
            flash("Producto añadido exitosamente!")

        return redirect("/productos")  

    productos = Productos.query.all()
    return render_template("productos.html", productos=productos)

@productos_blueprint.route("/productos/editar/<int:id>", methods=["GET"])
def editarProducto(id):
    producto = Productos.query.get(id) 
    return render_template("productos.html", producto=producto, productos=Productos.query.all())


@productos_blueprint.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminarProducto(id):
    producto = Productos.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado exitosamente!")
    return redirect("/productos")