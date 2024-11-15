from flask import Blueprint, redirect, render_template, url_for, request, session, flash
from decimal import Decimal
from models.membresias import Membresias
from database import db

membresias_blueprint = Blueprint('membresias_blueprint', __name__)

@membresias_blueprint.route("/membresias", methods=["POST", "GET"])
def membresiasCrud():
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")

    if request.method == "POST":
        tipomembresia = request.form['tipo_membresia']
        costo = Decimal(request.form['costoMembresia'])
        membresia_id = request.form.get('membresia_id')
        
        if membresia_id:  
            membresia = Membresias.query.get(membresia_id)
            membresia.tipomembresia = tipomembresia
            membresia.costo = costo
            db.session.commit()
            flash("Membresía actualizada exitosamente!")
        else:
            nueva_membresia = Membresias(tipomembresia, costo)
            db.session.add(nueva_membresia)
            db.session.commit()
            flash("Membresía añadida exitosamente!")
            
        return redirect("/membresias")

    membresias = Membresias.query.all()
    return render_template("membresias.html", membresias=membresias)

@membresias_blueprint.route("/membresias/editar/<int:id>", methods=["GET"])
def editarMembresia(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    membresia = Membresias.query.get(id)
    membresias = Membresias.query.filter_by(habilitado=True).all()
    return render_template("membresias.html", membresia=membresia, membresias=membresias)

@membresias_blueprint.route("/membresias/desactivar/<int:id>", methods=["POST"])
def desactivarMembresia(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    membresia = Membresias.query.get(id)
    membresia.habilitado = False
    db.session.commit()
    flash("Membresía desactivada exitosamente!")
    return redirect("/membresias")

@membresias_blueprint.route("/membresias/reactivar/<int:id>", methods=["POST"])
def reactivarMembresia(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    membresia = Membresias.query.get(id)
    membresia.habilitado= True
    db.session.commit()
    flash("Membresia reactivada exitosamente!")
    return redirect("/membresias")