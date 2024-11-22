from flask import Blueprint,Flask, redirect, url_for, render_template, request, session, flash, jsonify, current_app
from flask_mail import * 
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta
from decimal import Decimal
from models.empleados import Empleado
from models.empleados import Rol
from database import db
from sqlalchemy import text
import requests
import matplotlib
import io
from datetime import datetime
matplotlib.use('Agg')  
import calendar
import matplotlib.pyplot as plt

from io import BytesIO
import base64

import random


main_blueprint = Blueprint('main_blueprint', __name__)


@main_blueprint.route("/")
def home():
    if "email" not in session:
        flash("Debes iniciar sesión")
        return redirect(url_for("main_blueprint.login"))  
    
    if session["rol"] == "Administrador":
        c_fecha_inicio = request.args.get("c_fecha_inicio", "1800-01")
        c_fecha_fin = request.args.get("c_fecha_fin", "2100-12")
        e_fecha_inicio = request.args.get("e_fecha_inicio", "1800-01")
        e_fecha_fin = request.args.get("e_fecha_fin", "2100-12")

        if(c_fecha_inicio == ''):
            c_fecha_inicio = "1800-01"
        if(c_fecha_fin == ''):
            c_fecha_fin = "2100-12"
        if(e_fecha_inicio == ''):
            e_fecha_inicio = "1800-01"
        if(e_fecha_fin == ''):
            e_fecha_fin = "2100-12"

        c_fecha_inicio += "-01"
        c_fecha_fin = obtener_ultimo_dia_mes(c_fecha_fin)
        e_fecha_inicio += "-01"
        e_fecha_fin = obtener_ultimo_dia_mes(e_fecha_fin)
        
        compras_totales = obtener_compras_totales_por_mes()
        entregas_totales = obtener_entregas_totales_por_mes()
        #obtencion de graficos de proveedores de maquinas
        ventas_por_proveedor = obtener_ventas_totales_por_proveedor()
        nombresProveedorPastel = []
        totalesProveedoPastel = []
        for row in ventas_por_proveedor:
            nombresProveedorPastel.append(row.proveedor)
            totalesProveedoPastel.append(row.total)
            
        
        #obtencion de graficos de proveedores de productos
        ventas_por_proveedor_producto = obtener_ventas_totales_por_proveedor_producto()
        nombresProveedorPastelProducto = []
        totalesProveedoPastelProducto = []
        for row in ventas_por_proveedor_producto:
            nombresProveedorPastelProducto.append(row.proveedor)
            totalesProveedoPastelProducto.append(row.total)
            
        #obtencion de                                                                                                                 
        compras_filtradas = filtrar_por_fechas(compras_totales, c_fecha_inicio, c_fecha_fin)
        entregas_filtradas = filtrar_por_fechas(entregas_totales, e_fecha_inicio, e_fecha_fin)
        
        meses_compras = [fila[0] for fila in compras_filtradas] 
        totales_compras = [fila[1] for fila in compras_filtradas] 
        img1 = BytesIO()
        crear_grafico(meses_compras, totales_compras, img1, "Ganancias mensuales de ventas de productos")  
        img1.seek(0) 

        meses_entregas = [fila[0] for fila in entregas_filtradas] 
        totales_entregas = [fila[1] for fila in entregas_filtradas] 
        img2 = BytesIO()
        crear_grafico(meses_entregas, totales_entregas, img2, "Dinero gastado en suministros mensualmente")  
        img2.seek(0) 
        
        #obtencion de grafico pastel de proveedores
        img3 = BytesIO()
        grafico_pastel(nombresProveedorPastel, totalesProveedoPastel, img3, "Porcentaje de proveedores mas solicitados para maquinas")  
        img3.seek(0) 
        
        #obtencion de grafico pastel de proveedores y productos
        img5 = BytesIO()
        grafico_pastel(nombresProveedorPastelProducto, totalesProveedoPastelProducto, img5, "Porcentaje de proveedores mas solicitados para productos")
        img5.seek(0)

        resultados = obtener_suma_venta_productos()
        ventas_por_producto, meses = procesar_datos_productos(resultados)

        # Seleccionar los tres productos más vendidos
        productos_top = sorted(ventas_por_producto.keys(), 
                            key=lambda p: sum(ventas_por_producto[p]), 
                            reverse=True)[:3]
        ventas_top = [ventas_por_producto[producto] for producto in productos_top]

        # Crear el gráfico
        img4 = crear_stackplot_base64(*ventas_top, meses=meses, labels=productos_top)
        
        v_rol = "Eres un " + session['rol'] if session.get('rol') else "Aún no te asignaron un rol"
        img1 = base64.b64encode(img1.getvalue()).decode('utf-8')  
        img2 = base64.b64encode(img2.getvalue()).decode('utf-8')
        img3 = base64.b64encode(img3.getvalue()).decode('utf-8')
        img5 = base64.b64encode(img5.getvalue()).decode('utf-8')
        return render_template("index.html", img1=img1, img2=img2, rol=v_rol, img3=img3, img4=img4,img5=img5, nombre=session.get('usuario'))
    else:
        return redirect("tareasCom")

@main_blueprint.route("/login", methods=["POST", "GET"]) 
def login():
    mail = current_app.extensions['mail']
    if request.method == "POST":
        session.permanent = True
        email = request.form["email"]
        password = request.form["password"]
        

        found_user = Empleado.query.filter_by(email=email).first()
        
        if found_user:
            if check_password_hash(found_user.password, password):
                codigo = codigo_verificacion()
                session["codigo"] = codigo
                session["email_verificacion"] = found_user.email

                msg = Message(
                    "Tu código de verificación",
                    sender="quantumcodersunivalle@gmail.com",
                    recipients=[found_user.email]
                )
                msg.body = f"Tu código de verificación es: {codigo}"
                mail.send(msg)
                recaptcha_response = request.form.get('g-recaptcha-response')
    
                data = {
                    'secret': "6LeEJYAqAAAAAK8HoU_2F6E8nJUwypVorl9AUcdn",
                    'response': recaptcha_response
                }
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()

                if not result.get('success'):
                    flash('Verificación de reCAPTCHA fallida. Por favor, inténtalo de nuevo.')
                    return redirect("login")
                return redirect(url_for("main_blueprint.verificar"))
            else:
                flash("Contraseña incorrecta")
                return redirect("login") 
        else:
            flash("Usuario no encontrado")
            return redirect("login") 

    else:
        if "email" in session: 
            flash("Ya iniciaste sesión!")
            return redirect(url_for("main_blueprint.home"))

    return render_template("login.html")

@main_blueprint.route("/empleados/verificar", methods=["POST", "GET"])
def verificar():
    if "codigo" not in session:
        flash("Error, no iniciaste sesion")
        return redirect("login") 
    if request.method == "POST":
        code = request.form["code"]
        if code == session["codigo"]:
            found_user = Empleado.query.filter_by(email=session["email_verificacion"]).first()
            if(found_user.cambiopassword == False):
                return render_template("password.html", empleado=found_user)
            session["email"] = found_user.email
            session["usuario"] = found_user.nombre + " " +  found_user.apellido
            session["empleado_id"] = found_user.idempleado
            rol = Rol.query.get(found_user.idrol)
            session["rol"] = rol.descripcion
            flash("Inicio de sesión correcto" )
            if session["rol"] == "Administrador":
                return redirect("/")
            else:
                return redirect("tareasCom")
        else:
            flash("Codigo incorrecto")
        return redirect("/login") 
    return render_template("verificacion.html", emailV = session["email_verificacion"])



@main_blueprint.route("/logout")
def logout():
    flash("You have been logged out!", "info")
    session.pop("nombre", None)
    session.pop("email", None)
    session.pop("empleado_id", None)
    return redirect("login")


@main_blueprint.route("/inicio")
def inicio():
    return render_template("inicio.html")


@main_blueprint.route("/password", methods=["POST"])
def password():
    if request.method == "POST":
        idemp = request.form["idemp"]
        passw = request.form["pass1"]
        emp = Empleado.query.get(idemp) 
        
        if emp:
            hashed_password = generate_password_hash(passw)
            
            emp.password = hashed_password
            
            emp.cambiopassword = True
            
            db.session.commit()
            session["email"] = emp.email
            session["usuario"] = emp.nombre + " " +  emp.apellido
            session["idempleado"] = emp.idempleado
            flash("Contraseña cambiada con éxito", "success")
            return redirect(url_for("main_blueprint.home"))
        else:
            flash("Empleado no encontrado", "danger")
            return redirect(url_for("main_blueprint.login"))


def codigo_verificacion():
    return str(random.randint(100000, 999999))



def procesar_datos_productos(resultados):
    productos = {}
    meses = sorted(set(row[2] for row in resultados))  # Extraer meses únicos y ordenarlos

    for producto, num_ventas, mes in resultados:
        if producto not in productos:
            productos[producto] = {mes: num_ventas}
        else:
            productos[producto][mes] = num_ventas

    # Crear listas de ventas por mes para cada producto
    ventas_por_producto = {
        producto: [productos[producto].get(mes, 0) for mes in meses]
        for producto in productos
    }

    return ventas_por_producto, meses

# Filtrado por fechas
def filtrar_por_fechas(datos, fecha_inicio, fecha_fin):
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    datos_filtrados = [
        fila for fila in datos 
        if fecha_inicio <= datetime.strptime(fila[0], "%Y-%m") <= fecha_fin
    ]
    return datos_filtrados
def obtener_ultimo_dia_mes(fecha):
        # Separar año y mes
        anio, mes = map(int, fecha.split("-"))
        # Obtener el último día del mes
        _, ultimo_dia = calendar.monthrange(anio, mes)
        return f"{fecha}-{ultimo_dia:02d}"




# Imagenes
def obtener_compras_totales_por_mes():
    resultados = db.session.execute(text("SELECT * FROM obtener_compras_totales_por_mes();")).fetchall()
    return resultados
def obtener_entregas_totales_por_mes():
    resultados = db.session.execute(text("SELECT * FROM obtener_entregas_totales_por_mes();")).fetchall()
    return resultados
def obtener_ventas_totales_por_proveedor():
    resultados = db.session.execute(text("select * from obtener_ventas_maquinas_por_proveedor();")).fetchall()
    return resultados
def obtener_ventas_totales_por_proveedor_producto():
    resultados = db.session.execute(text("select * from obtener_ventas_productos_por_proveedor();")).fetchall()
    return resultados
def obtener_suma_venta_productos():
    resultados = db.session.execute(text("select * from obtener_productos_mas_vendidos();")).fetchall()
    return resultados




def crear_grafico(meses, totales, img, titulo, color='red', xlabel='Meses', ylabel='Valores (bs.)', facecolor='#ffffff'):
    plt.figure(figsize=(5, 3))
    plt.bar(meses, totales, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(titulo)
    plt.gca().set_facecolor(facecolor)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(img, format='png')
    plt.close()

import matplotlib.pyplot as plt

def grafico_pastel(nombres, cantidades, img, titulo):
    colores = ['#c81d25', '#087e8b', '#0b3954']
    maximo = max(cantidades)
    explode = []
    for cant in cantidades:
        if cant == maximo:
            explode.append(0.1)
        else:
            explode.append(0)
    if len(nombres) != len(cantidades):
        raise ValueError("Los arreglos de nombres y cantidades deben tener la misma longitud.")
    plt.figure(figsize=(13, 10))
    # Aumentar el tamaño de los labels del gráfico
    plt.pie(cantidades, explode=explode, labels=nombres, autopct='%1.1f%%', startangle=140, colors=colores,textprops={'fontsize': 24}
    )
    # Aumentar el tamaño del título
    plt.title(titulo, pad=30, loc="center", fontsize=30)
    plt.axis('equal')
    plt.savefig(img, format='png')
    plt.close()


def crear_stackplot_base64(*ventas, meses, labels):
    colores = ['#c81d25', '#087e8b', '#0b3954']
    plt.figure(figsize=(5, 3))
    plt.stackplot(meses, *ventas, labels=labels, colors=colores)
    plt.title('Ventas de productos por mes')
    plt.xlabel('Mes')
    plt.ylabel('Cantidad de ventas')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()

    # Convertir la imagen a Base64
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')
    return img_base64
