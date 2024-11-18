from flask import Blueprint, Flask, redirect, url_for, render_template, request, session, flash, jsonify
from datetime import timedelta
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy 
from models.maquinas import Maquinas
from models.nombreMaquina import NombreMaquinas
from models.proveedores import Proveedores
from models.compramaquina import CompraMaquina
from models.detallecompramaquina import DetalleCompraMaquina
from database import db

maquinas_blueprint = Blueprint('maquinas_blueprint', __name__)

@maquinas_blueprint.route("/maquinas", methods=["POST", "GET"])
def maquinas():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    return render_template("verMaquinas.html", maquinas=Maquinas.query.all(), nombres=NombreMaquinas.query.all(), proveedores=Proveedores.query.all())
    
@maquinas_blueprint.route("/comprarmaquinas", methods=["POST", "GET"])
def maquinasCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
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
    return render_template("comprarMaquinas.html", maquinas=maquinas, nombres=NombreMaquinas.query.all(), proveedores=Proveedores.query.all())