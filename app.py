from flask import Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 

import os

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://quantumcoders_user:YFq8LXNKyaDgSJkFc0OGk9GwgfGTOlsj@dpg-cs2hv4bqf0us73a8h0fg-a.virginia-postgres.render.com/quantumcoders"

app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Productos(db.Model):
    __tablename__ = 'productos'  # Nombre de la tabla en la base de datos

    _id = db.Column("idp", db.Integer, primary_key=True, autoincrement=True)  # Columna de identificación
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del producto
    preciov = db.Column(db.Numeric(10, 2), nullable=False)  # Precio de venta, tipo decimal
    stock = db.Column(db.Integer, nullable=False)  # Stock disponible

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.preciov = precio
        self.stock = stock
    def __repr__(self):
        return f'<Producto {self.nombre}, Precio: {self.previov}, Stock: {self.stock}>'
class Proveedores(db.Model):
    __tablename__ = 'proveedores'  # Nombre de la tabla en la base de datos

    _id = db.Column("idproveedor", db.Integer, primary_key=True, autoincrement=True)  # Columna de identificación
    nombre = db.Column(db.String(30), nullable=False)  # Nombre del producto
    telefono = db.Column(db.String(9), nullable=False)  # Precio de venta, tipo decimal
    correo = db.Column(db.String(50), nullable=False)  # Stock disponible

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.telefono = precio
        self.correo = stock
    def __repr__(self):
        return f'<Proveedor {self.nombre}, Telefono: {self.telefono}, Correo: {self.correo}>'
# Crear las tablas antes de que arranque la aplicación

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"]) 
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["nm"]
        session["user"] = user

        found_user = users.query.filter_by(name=user).first()
        
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, "")
            db.session.add(usr)
            db.session.commit() 

        flash("Login successful")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!")
            return redirect(url_for("user"))
        return render_template("login.html")

@app.route("/user", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            db.session.commit() 
            flash("Email was saved")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", email=email)
    else:
        flash("You are not logged in!")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/test")
def test():
    return render_template("new.html")





# RUTAS DE LOS CRUDS

@app.route("/productos", methods=["POST", "GET"])
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

@app.route("/productos/editar/<int:id>", methods=["GET"])
def editarProducto(id):
    producto = Productos.query.get(id) 
    return render_template("productos.html", producto=producto, productos=Productos.query.all())


@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminarProducto(id):
    producto = Productos.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado exitosamente!")
    return redirect("/productos")

#Proveedores (Pagina Principal)
@app.route("/proveedores", methods=["POST", "GET"])
def proveedoresCrud():
    if request.method == "POST":
        nombre = request.form['nombreProveedor']
        telefono = request.form['telefonoProveedor']  
        correo = request.form['correoProveedor']
        proveedor_id = request.form.get('proveedor_id')  
        if proveedor_id: 
            proveedor = Proveedores.query.get(proveedor_id)
            proveedor.nombre = nombre
            proveedor.telefono = telefono
            proveedor.correo = correo
            db.session.commit() 
            flash("Proveedor editado exitosamente!")
        else:
            nuevo_proveedor = Proveedores(nombre, telefono, correo)
            db.session.add(nuevo_proveedor)
            db.session.commit() 
            flash("Proveedor añadido exitosamente!")
        return redirect("/proveedores")
    proveedores = Proveedores.query.all()
    return render_template("proveedores.html", proveedores=proveedores)
#Proveedores (Edicion)
@app.route("/proveedores/editar/<int:id>", methods=["GET"])
def editarProveedor(id):
    proveedor = Proveedores.query.get(id) 
    return render_template("proveedores.html", proveedor=proveedor, proveedores=Proveedores.query.all())

@app.route("/proveedores/eliminar/<int:id>", methods=["POST"])
def eliminarProveedor(id):
    proveedor = Proveedores.query.get(id)
    db.session.delete(proveedor)
    db.session.commit()
    flash("Proveedor eliminado exitosamente!")
    return redirect("/proveedores")

if __name__ == "__main__":
    app.run(debug=True)


class Empleado(db.Model):
    __tablename__ = 'empleados'  # Nombre de la tabla en la base de datos

    idempleado = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(100), nullable=True)
    carnet = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(15), nullable=True)
    sueldo = db.Column(db.Numeric(10, 2), nullable=True)

    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido}>'


@app.route('/empleados')
def listar_empleados():
    empleados = obtener_todos_los_empleados()  # Implementar esta función para obtener los empleados de la BD
    return render_template('empleados.html', empleados=empleados)


@app.route('/empleados', methods=['POST'])
def agregar_actualizar_empleado():
    empleado_id = request.form.get('empleado_id')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    direccion = request.form.get('direccion')
    carnet = request.form.get('carnet')
    telefono = request.form.get('telefono')
    sueldo = request.form.get('sueldo')
    
    if empleado_id:  # Actualizar empleado
        actualizar_empleado(empleado_id, nombre, apellido, direccion, carnet, telefono, sueldo)
        flash('Empleado actualizado correctamente')
    else:  # Agregar nuevo empleado
        agregar_empleado(nombre, apellido, direccion, carnet, telefono, sueldo)
        flash('Empleado añadido correctamente')
    
    return redirect('/empleados')


@app.route('/empleados/editar/<int:empleado_id>')
def editar_empleado(empleado_id):
    empleado = obtener_empleado_por_id(empleado_id)  # Implementar esta función
    return render_template('empleados.html', empleado=empleado)


@app.route('/empleados/eliminar/<int:empleado_id>', methods=['POST'])
def eliminar_empleado(empleado_id):
    eliminar_empleado_por_id(empleado_id)  # Implementar esta función
    flash('Empleado eliminado correctamente')
    return redirect('/empleados')






