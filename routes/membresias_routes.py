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
        tipomembresia = request.form['tipo_membresia'].strip()
        costo = Decimal(request.form['costoMembresia'])
        duracion = request.form['duracionMemebresia']
        membresia_id = request.form.get('membresia_id')

        errores = []

        if not tipomembresia or len(tipomembresia) < 3:
            errores.append("El tipo de membresia es obligatorio.")
            flash("El tipo de membresia es obligatorio.")
        else:
            membresia_existente = Membresias.query.filter_by(tipomembresia=tipomembresia).first()
            if membresia_existente and (not membresia_id or membresia_existente.idmembresia != int(membresia_id)):
                errores.append(f"Ya existe una membresia con el nombre '{tipomembresia}'.")
                flash("Ya existe una membresia con ese nombre")
        
         # Validar costo
        try:
            costo = Decimal(costo)
            if costo <= 0:
                errores.append("El costo debe ser un valor positivo.")
        except:
            errores.append("El costo debe ser un número válido.")

        # Validar duración
        if not duracion.isdigit() or int(duracion) <= 0:
            errores.append("La duración debe ser un número entero positivo.")
        else:
            duracion = int(duracion)

        if errores:
            for error in errores:
                flash(error)
            return redirect("/membresias")
        
        if membresia_id:  # Edición
            membresia = Membresias.query.get(membresia_id)
            if membresia:
                membresia.tipomembresia = tipomembresia
                membresia.costo = costo
                membresia.duracion = duracion
                db.session.commit()
                flash("Membresía actualizada exitosamente!")
            else:
                flash("No se encontró la membresía a editar.")
        else:  # Creación
            nueva_membresia = Membresias(
                tipomembresia=tipomembresia,
                costo=costo,
                duracion=duracion,
                habilitado=True
            )
            db.session.add(nueva_membresia)
            db.session.commit()
            flash("Membresía añadida exitosamente!")

        return redirect("/membresias")

    membresias = Membresias.query.all()
    return render_template("membresias.html", membresias=membresias, rol = session["rol"])

@membresias_blueprint.route("/membresias/editar/<int:id>", methods=["GET"])
def editarMembresia(id):
    if "usuario" not in session:
        flash("Debes iniciar sesión")
        return redirect("/login")
    membresia = Membresias.query.get(id)
    membresias = Membresias.query.filter_by(habilitado=True).all()
    return render_template("membresias.html", membresia=membresia, membresias=membresias, rol = session["rol"])

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