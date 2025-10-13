"""Punto de entrada principal de la aplicación FitFlow"""
import os
from flask import Flask
from dotenv import load_dotenv
from src.config.database import init_db

# Cargar variables de entorno
load_dotenv()


def create_app():
    """
    Factory function para crear y configurar la aplicación Flask.
    
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///fitflow.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints (controladores) aquí cuando estén implementados
    # from src.controllers import admin_bp, socio_bp
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(socio_bp)
    
    @app.route('/')
    def index():
        return {
            'message': 'FitFlow API - Sistema de Gestión para Gimnasios',
            'version': '1.0.0',
            'status': 'active'
        }
    
    @app.route('/health')
    def health():
        """Endpoint para verificar el estado del servicio"""
        return {'status': 'healthy'}
    
    return app


def init_database():
    """Inicializa la base de datos con datos de ejemplo"""
    from datetime import time
    from src.models import (
        PlanMembresia, Entrenador, Horario, Clase
    )
    from src.utils.enums import DiaSemana
    from src.config.database import db
    
    app = create_app()
    
    with app.app_context():
        # Crear tablas
        db.create_all()
        
        # Verificar si ya hay datos
        if PlanMembresia.query.first():
            print("La base de datos ya contiene datos.")
            return
        
        print("Inicializando base de datos con datos de ejemplo...")
        
        # Crear planes
        plan_full = PlanMembresia(
            titulo="Plan Full",
            descripcion="Acceso ilimitado a todas las clases y servicios del gimnasio",
            precio=15000.0
        )
        
        plan_musculacion = PlanMembresia(
            titulo="Plan Musculación",
            descripcion="Acceso a sala de musculación y clases funcionales",
            precio=10000.0
        )
        
        db.session.add(plan_full)
        db.session.add(plan_musculacion)
        
        # Crear entrenadores
        entrenador1 = Entrenador(
            nombre="María",
            apellido="González",
            email="maria.gonzalez@fitflow.com",
            especialidad="Yoga y Pilates"
        )
        
        entrenador2 = Entrenador(
            nombre="Carlos",
            apellido="Rodríguez",
            email="carlos.rodriguez@fitflow.com",
            especialidad="Entrenamiento Funcional"
        )
        
        db.session.add(entrenador1)
        db.session.add(entrenador2)
        
        # Crear horarios
        horario1 = Horario(
            dia_semana=DiaSemana.LUNES,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )
        
        horario2 = Horario(
            dia_semana=DiaSemana.MIERCOLES,
            hora_inicio=time(18, 0),
            hora_fin=time(19, 30)
        )
        
        db.session.add(horario1)
        db.session.add(horario2)
        db.session.commit()
        
        # Crear clases
        clase1 = Clase(
            titulo="Yoga Matutino",
            descripcion="Sesión de yoga para comenzar el día con energía",
            cupo_maximo=20,
            entrenador=entrenador1,
            horario=horario1
        )
        
        clase2 = Clase(
            titulo="Funcional Intenso",
            descripcion="Entrenamiento funcional de alta intensidad",
            cupo_maximo=15,
            entrenador=entrenador2,
            horario=horario2
        )
        
        db.session.add(clase1)
        db.session.add(clase2)
        
        # Asociar clases a planes
        plan_full.clases.append(clase1)
        plan_full.clases.append(clase2)
        plan_musculacion.clases.append(clase2)
        
        db.session.commit()
        
        print("✓ Base de datos inicializada correctamente")
        print(f"✓ Creados {len([plan_full, plan_musculacion])} planes")
        print(f"✓ Creados {len([entrenador1, entrenador2])} entrenadores")
        print(f"✓ Creadas {len([clase1, clase2])} clases")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        init_database()
    else:
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
