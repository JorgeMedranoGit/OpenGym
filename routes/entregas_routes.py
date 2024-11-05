from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify
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

@entregas_blueprint.route("/entregas" , methods=['GET', 'POST'])
def entregaCrud():
    if "usuario" not in session:
       flash("Debes iniciar sesión")
       return redirect("/login")
    entregas = obtenerEntregas()
    estados = obtener_todos_los_estados()
    for entrega in entregas:
        id = entrega['identrega']
        total = db.session.execute(text('SELECT calcular_total_entrega(:idC)'), {'idC': id}).scalar()
        estado = db.session.execute(text('SELECT devolver_ultimo_estado(:idC)'),{'idC': id}).scalar()
        entrega['total'] = total if total is not None else 0
        entrega['estado'] = estado if estado is not None else "Pendiente"
        entrega['fechaestado'] = db.session.execute(
            text('SELECT es.fechaestado FROM entregaestado es WHERE identrega = :identrega ORDER BY idestado DESC'),
            {'identrega': id}  # Aquí pasamos el valor correctamente
        ).scalar()
        if entrega['fechaestado'] is not None:
            entrega['fechaestado'] = entrega['fechaestado'].strftime("%d/%m/%Y")
        else:
        # Manejo cuando fechaestado es None, asignar un valor por defecto si es necesario
            entrega['fechaestado'] = "Fecha no disponible"
    return render_template("entregas.html", entregas=entregas, estados = estados)

@entregas_blueprint.route("/entregas/agregar", methods=['GET', 'POST'])
def formEntrega():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if request.method == 'GET':
        proveedores = obtenerTodoslosProveedores()
        productos = obtenerTodoslosProductos()
        return render_template("entregasForm.html", proveedores=proveedores, productos=productos)

    if request.method == 'POST':
        fechapedido = request.form['fechapedido']
        metodopago = request.form['metodopago']
        idproveedor = request.form['idproveedor']

        entregaN = Entregas(fechapedido=fechapedido, metodopago=metodopago, idproveedor=idproveedor)
        db.session.add(entregaN)  # Añadir la entrega a la sesión antes de hacer commit
        db.session.commit()  # Insertar la entrega y obtener el id

        idEntrega = entregaN.identrega  # Obtener el id después de hacer commit

        estadoN = EntregaEstado(fechaestado=datetime.now(), identrega=idEntrega, idestado=1)
        db.session.add(estadoN)
        db.session.commit()

        cantidades = request.form.getlist('cantidad[]')  # Obtener lista de cantidades
        preciosCompras = request.form.getlist('precio[]')  # Obtener lista de precios

        productos = request.form.getlist('idp[]')  # Cambia 'producto[]' a 'idp[]'
        for idp, cantidad, precio in zip(productos, cantidades, preciosCompras):
            if idp.strip() and int(cantidad) > 0 and float(precio) > 0:
                detalle = DetalleEntregas(cantidad=int(cantidad), preciocompra=float(precio), identrega=idEntrega, idproducto=idp)
                db.session.add(detalle)
        db.session.commit()
        flash("Entrega agregada exitosamente!")
        return redirect("/entregas")

    

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
        
        db.session.commit()
        flash("Estado de la entrega actualizado exitosamente", "success")
    else:
        flash("No se pudo actualizar el estado de la entrega" + entrega_id + " Estado: " + estado_id, "danger")

    return redirect(url_for("entregas_blueprint.entregaCrud"))



def obtenerEntregas():
    entregas = Entregas.query.all()
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

