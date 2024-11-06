# Dependencias
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from database import init_app, db


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


# Inicialización de la app.
app = Flask(__name__)
# -- Configuración de la base de datos mediante Config() donde se encuentra la base de datos
app.secret_key = "qc2024"
app.config.from_object(Config.Config()) 

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


if __name__ == "__main__":
    app.run(debug=True)


