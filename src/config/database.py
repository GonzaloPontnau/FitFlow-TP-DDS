"""Configuración de la base de datos"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Clase base para todos los modelos"""
    pass


db = SQLAlchemy(model_class=Base)


def init_db(app):
    """Inicializa la base de datos con la aplicación Flask"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
