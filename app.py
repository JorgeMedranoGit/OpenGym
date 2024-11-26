# Dependencias
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_mail import Mail
from database import init_app, db
from config import Email
import os
from dotenv import load_dotenv
from config import logging


# Resto del código de Flask



# Si descomentan esto basicamente estan abriendo la caja de pandora XD
# from models import clientes, empleados, productos, proveedores


# Importacion de rutas
from routes.clientes_routes import cliente_blueprint
from routes.empleados_routes import empleados_blueprint
from routes.productos_routes import productos_blueprint
from routes.proveedores_routes import proveedores_blueprint
from routes.compras_routes import compras_blueprint
from routes.entregas_routes import entregas_blueprint
from routes.estados_routes import estados_blueprint
from routes.main import main_blueprint
from routes.tareas_routes import tareas_blueprint
from routes.tareas_asignadas import tareas_asignadas_blueprint
from routes.membresias_routes import membresias_blueprint
from routes.maquinas_routes import maquinas_blueprint

from routes.mantenimientoRutas import mantenimiento_bp

from routes.sesiones_routes import session_blueprint

from routes.pagos_routes import pago_blueprint

from routes.impresion_route import impresion_blueprint

load_dotenv()


logging.configure_logging()

mail = Mail()

# Inicialización de la app.
app = Flask(__name__)
# -- Configuración de la base de datos mediante Config() donde se encuentra la base de datos
app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config.from_object(Config.Config()) 
app.config.from_object(Email.Email())

mail = Mail(app)



init_app(app)

# Registrar las rutas en la aplicación, los argumentos usados estan importados previamente en la importación de las rutas
app.register_blueprint(cliente_blueprint)
app.register_blueprint(empleados_blueprint)
app.register_blueprint(productos_blueprint)
app.register_blueprint(proveedores_blueprint)
app.register_blueprint(compras_blueprint)
app.register_blueprint(entregas_blueprint)
app.register_blueprint(estados_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(tareas_blueprint)
app.register_blueprint(tareas_asignadas_blueprint)
app.register_blueprint(membresias_blueprint)
app.register_blueprint(maquinas_blueprint)

app.register_blueprint(mantenimiento_bp)

app.register_blueprint(session_blueprint)

app.register_blueprint(pago_blueprint)

app.register_blueprint(impresion_blueprint)



# Manejo de errores para el error 500
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Manejo de errores para el error 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Manejo de excepciones generales
@app.errorhandler(Exception)
def handle_exception(e):
    # Aquí puedes registrar el error si lo deseas
    return render_template('500.html', error=str(e)), 500


if __name__ == "__main__":
    app.run(debug=True)


