from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://quantumcoders_user:YFq8LXNKyaDgSJkFc0OGk9GwgfGTOlsj@dpg-cs2hv4bqf0us73a8h0fg-a.virginia-postgres.render.com/quantumcoders"  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    return app
