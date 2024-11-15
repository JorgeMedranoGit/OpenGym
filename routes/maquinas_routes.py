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

@maquinas_blueprint.route("/comprarmaquinas", methods=["POST", "GET"])
def maquinasCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    
    if request.method == "POST":
        print("Entró en la ruta POST")
        try:
            data = request.get_json()  # Obtener los datos JSON
            maquinas = data.get('productos')
            idEmp = session['empleado_id']
            nuevComp = CompraMaquina(idEmp)
            db.session.add(nuevComp)
            db.session.commit()
            idComp = nuevComp._id
            idComp = 1
            print("CREAR COMPRA")
            for maquina in maquinas:
                idNomMaquina = maquina['idNombre']
                if(maquina['idNombre'] == '0'):
                    nomMaquina = NombreMaquinas(maquina['nombre'], maquina['codnom'], maquina['cantidad'])
                    db.session.add(nomMaquina);
                    db.session.commit();
                    idNomMaquina = nomMaquina._id
                    maquina['cantidad'] = 0;
                nomMaquina = NombreMaquinas.query.get(idNomMaquina);
                idProv = maquina['idProveedor']
                if(maquina['idProveedor'] == '0'):
                    newProv = Proveedores(maquina['proveedor'], maquina['telf'], maquina['correo'])
                    db.session.add(newProv);
                    db.session.commit();
                    idProv = newProv._id
                print("Insertando Maquina")
                for i in range(1, maquina['cantidad'] + 1):
                    newMaquina = Maquinas(maquina['tipoMaquina'], "Comprado", idNomMaquina, idEmp, idProv)
                    db.session.add(newMaquina);
                    db.session.commit();
                print("CREAR DETALLE")
                newDetalle = DetalleCompraMaquina(idComp, idNomMaquina, maquina['cantidad'], idProv, maquina['precioUnitario'])
                db.session.add(newDetalle);
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