from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.maquinas import Maquinas
from models.nombreMaquina import NombreMaquinas
from models.proveedores import Proveedores
from models.compramaquina import CompraMaquina
from models.detallecompramaquina import DetalleCompraMaquina
from sqlalchemy import text
from database import db

maquinas_blueprint = Blueprint('maquinas_blueprint', __name__)
@maquinas_blueprint.route("/maquinasImpres", methods=["POST", "GET"])
def printMaq():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    inicio = request.args.get('fechaInicio')
    fin = request.args.get('fechaFin')
    print(request.args.get('fechaInicio'))
    print(request.args.get('fechaFin'))
    if inicio == "" or fin == "":
        print("Mostrar todos los detalles")
        result = db.session.execute(text("select * from obtener_resumen_compras_totales();"))
    else:
        print("Mostrar los detalles filtrados")
        result = db.session.execute(text("SELECT * FROM obtener_resumen_compras(:fecha_inicio, :fecha_fin)"),{'fecha_inicio': inicio, 'fecha_fin': fin})
    compras = result.fetchall()
    tbody = []
    for fila in compras:
        fila_html = "<tr>"
        for valor in fila:
            fila_html += f"<td>{valor}</td>"
        fila_html += "</tr>"
        tbody.append(fila_html)
    thead_html = "<th>Fecha</th><th>ID</th><th>Nombre</th><th>Codigo</th><th>Total</th>"
    tbody_html = "".join(tbody)
    suma_total = 0.0
    for fila in compras:
        suma_total += fila[4]

    print("Suma total:", suma_total)


    suma_total = "<tr><td></td><td></td><td></td><td></td><td>" + str(suma_total) + "</td></tr>"

    session['thead'] = thead_html
    session['tbody'] = tbody_html
    session['extra'] = suma_total
    return redirect('/imprimir')
@maquinas_blueprint.route("/maquinas", methods=["POST", "GET"])
def maquinas():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    return render_template("verMaquinas.html", maquinas=Maquinas.query.all(), nombres=NombreMaquinas.query.all(), proveedores=Proveedores.query.all(), rol = session["rol"])
@maquinas_blueprint.route("/verComprasMaquinas", methods=["GET"])
def ver_compras_maquinas():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    try:
        # Llamar al procedimiento almacenado
        result = db.session.execute(text("SELECT * FROM obtenercomprasmaquinas()"))
        # Obtener los resultados
        compras = result.fetchall()

        # Llamar al procedimiento almacenado
        result = db.session.execute(text("SELECT * FROM obtenerdetallescomprasmaquinas()"))
        # Obtener los resultados
        detalles = result.fetchall()
        
        # Convertir los resultados a una lista de diccionarios
        compras_dict = []
        for row in compras:
            compras_dict.append({
                'idcompra': row.idcompra,
                'fecha': row.fecha,
                'proveedor': row.proveedor,
                'Gastos': row.gastos
            })
        detalles_dict = []
        for row in detalles:
            detalles_dict.append({
                'idcompra': row.idcompra,
                'fecha': row.fecha,
                'nombre': row.nombre,
                'codigo': row.codigomaquina,
                'proveedor': row.proveedor,
                'tipo': row.tipo,
                'gastos': row.gastos,
                'estado': row.estado,
                'total': row.total,
                'iddetalle': row.iddetalle
            })
        # Renderizar la plantilla con los resultados
        return render_template("verComprasMaquinas.html", compras=compras_dict, detalleCompras=detalles_dict, rol = session["rol"])

    except Exception as e:
        flash(f"Error al obtener las compras: {str(e)}")
        return redirect(url_for('maquinas_blueprint.maquinas'))
    
    
    
@maquinas_blueprint.route("/verDetalleCompra/<int:iddetalle>", methods=["GET"])
def ver_detalles_compra(iddetalle):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    try:
        # Llamar al procedimiento almacenado
        result = db.session.execute(text(f"SELECT * FROM obtener_maquinas_por_detalle(:iddetalle)"), {'iddetalle': iddetalle})
        # Obtener los resultados
        maquinas = result.fetchall()
        #Mapear los resultados
        maquinas_dict = []
        for row in maquinas:
            maquinas_dict.append({
                'idmaquina': row.idmaquina,
                'nombre': row.nombre,
                'codigo': row.codigomaquina,
                'tipo': row.tipo,
                'estado': row.estado
            })
        # Renderizar la plantilla con los resultados
        return render_template("verDetalleCompra.html", detalle=maquinas_dict, maquinas=maquinas_dict, rol = session["rol"])
    except Exception as e:
        flash(f"Error al obtener las maquinas: {str(e)}")
        return redirect(url_for('maquinas_blueprint.maquinas'))

@maquinas_blueprint.route("/confirmarEntregaDetalle/<int:iddetalle>", methods=["GET"])
def confirmar_entrega_detalle(iddetalle):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    try:
        Maquinas.actualizar_estado_maquinas(iddetalle)
        return redirect("/verComprasMaquinas")
    except Exception as e:
        flash(f"Error al obtener las maquinas: {str(e)}")
        return redirect(url_for('maquinas_blueprint.maquinas'))
    
@maquinas_blueprint.route("/comprarmaquinas", methods=["POST", "GET"])
def maquinasCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    if session['rol'] != "Administrador":
        return redirect("/tareasCom")
    if request.method == "POST":
        print("Entró en la ruta POST")
        try:
            data = request.get_json()  # Obtener los datos JSON
            proveedor = data.get('proveedor')
            maquinas = data.get('productos')
            idEmp = session['empleado_id']
            print(proveedor);
            idProv = proveedor['idProveedor']
            if(proveedor['idProveedor'] != '0'):
                print('conocido')
            else:
                print(proveedor['nombreProveedor']);
                print(proveedor['telfProveedor']);
                print(proveedor['correoProveedor']);
                newProv = Proveedores(proveedor['nombreProveedor'], proveedor['telfProveedor'], proveedor['correoProveedor'])
                db.session.add(newProv);
                db.session.commit();
                idProv = newProv._id
            nuevComp = CompraMaquina(idEmp, idProv)
            db.session.add(nuevComp)
            db.session.commit()
            idComp = nuevComp._id
            for maquina in maquinas:
                print("Insertando Nombre Maquina")
                idNomMaquina = maquina['idNombre']
                cantidad = maquina['cantidad'];
                if(maquina['idNombre'] == '0'):
                    nomMaquina = NombreMaquinas(maquina['nombre'], maquina['codnom'], maquina['cantidad'])
                    db.session.add(nomMaquina);
                    db.session.commit();
                    idNomMaquina = nomMaquina._id
                    maquina['cantidad'] = 0;
                nomMaquina = NombreMaquinas.query.get(idNomMaquina);
                print("CREAR DETALLE")
                newDetalle = DetalleCompraMaquina(idComp, cantidad, maquina['precioUnitario'])
                db.session.add(newDetalle);
                db.session.commit();
                idDetalle = newDetalle._id
                for i in range(1, cantidad + 1):
                    print("Insertando Maquina")
                    newMaquina = Maquinas(maquina['tipoMaquina'], "Comprado", idNomMaquina, idDetalle)
                    db.session.add(newMaquina);
                    db.session.commit();
                nomMaquina.cantidad = nomMaquina.cantidad + maquina['cantidad']
                db.session.commit();
                
            flash("Compra realizada con éxito!")
            return jsonify({"message": "Compra realizada con éxito!"}), 200
        except Exception as e:
            flash(f"Error: {str(e)}")
            print(str(e))
            return jsonify({"error": str(e)}), 500

    maquinas = Maquinas.query.all()
    return render_template("comprarMaquinas.html", maquinas=maquinas, nombres=NombreMaquinas.query.all(), proveedores=Proveedores.query.filter(Proveedores.habilitado == True).all(), rol = session["rol"])