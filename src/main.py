"""Punto de entrada principal de la aplicación FitFlow"""
from flask import Flask, jsonify
from src.config.database import init_db
from src.config.settings import settings
from src.core.logging_config import setup_logging, get_logger
from src.api.controllers import socio_bp, clase_bp, reserva_bp, pago_bp
from src.exceptions.base_exceptions import FitFlowException

# Configurar logging
setup_logging(log_level=settings.app.log_level)
logger = get_logger(__name__)


def create_app():
    """
    Factory function para crear y configurar la aplicación Flask.
    
    Aplica el patrón Application Factory para facilitar testing
    y configuración por ambiente.
    
    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    
    # Configuración desde settings centralizados
    app.config['SECRET_KEY'] = settings.app.secret_key
    app.config['DEBUG'] = settings.app.debug
    app.config['TESTING'] = settings.app.testing
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database.url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = settings.database.echo
    
    logger.info("Inicializando aplicación FitFlow...")
    
    # Inicializar base de datos
    init_db(app)
    logger.info("Base de datos inicializada")
    
    # Registrar blueprints (controladores REST)
    app.register_blueprint(socio_bp)
    app.register_blueprint(clase_bp)
    app.register_blueprint(reserva_bp)
    app.register_blueprint(pago_bp)
    logger.info("Controladores REST registrados")
    
    # Manejador global de errores
    @app.errorhandler(FitFlowException)
    def handle_fitflow_exception(error):
        """Maneja excepciones personalizadas del sistema"""
        logger.error(f"FitFlowException: {error.message}")
        return jsonify(error.to_dict()), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404"""
        return jsonify({
            'error': {
                'type': 'NOT_FOUND',
                'message': 'Recurso no encontrado',
                'details': {}
            }
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores internos del servidor"""
        logger.exception("Error interno del servidor")
        return jsonify({
            'error': {
                'type': 'INTERNAL_ERROR',
                'message': 'Error interno del servidor',
                'details': {}
            }
        }), 500
    
    # Endpoints informativos
    @app.route('/')
    def index():
        """Endpoint raíz con información de la API"""
        return jsonify({
            'message': 'FitFlow API - Sistema de Gestión para Gimnasios',
            'version': '2.0.0',
            'status': 'active',
            'endpoints': {
                'socios': '/api/socios',
                'clases': '/api/clases',
                'reservas': '/api/reservas',
                'pagos': '/api/pagos',
                'health': '/health'
            }
        })
    
    @app.route('/health')
    def health():
        """Endpoint para verificar el estado del servicio"""
        return jsonify({
            'status': 'healthy',
            'version': '2.0.0',
            'database': 'connected'
        })
    
    logger.info("Aplicación FitFlow configurada correctamente")
    return app


def init_database():
    """
    Inicializa la base de datos con datos de ejemplo.
    
    Crea las tablas y carga datos iniciales para desarrollo/testing.
    """
    logger.info("Inicializando base de datos con datos de ejemplo...")
    app = create_app()
    
    with app.app_context():
        from datetime import time
        from src.config.database import db
        from src.models import (
            PlanMembresia, Socio, Entrenador,
            Horario, Clase
        )
        from src.utils.enums import DiaSemana
        
        # Crear todas las tablas
        db.create_all()
        logger.info("Tablas de base de datos creadas")
        
        # Verificar si ya hay datos
        if PlanMembresia.query.first():
            logger.info("Base de datos ya contiene datos")
            return
        
        # Crear planes de membresía
        plan_basico = PlanMembresia(
            "Plan Básico",
            "Acceso a gimnasio y clases grupales básicas",
            10000.0
        )
        plan_premium = PlanMembresia(
            "Plan Premium",
            "Acceso completo a gimnasio y todas las clases",
            20000.0
        )
        
        db.session.add_all([plan_basico, plan_premium])
        db.session.commit()
        logger.info("Planes de membresía creados")
        
        # Crear entrenadores
        entrenador1 = Entrenador(
            "Carlos",
            "Rodríguez",
            "Instructor de Spinning"
        )
        entrenador2 = Entrenador(
            "María",
            "García",
            "Profesora de Yoga"
        )
        
        db.session.add_all([entrenador1, entrenador2])
        db.session.commit()
        logger.info("Entrenadores creados")
        
        # Crear horarios y clases
        horario1 = Horario(DiaSemana.LUNES, time(18, 0), time(19, 0))
        horario2 = Horario(DiaSemana.MIERCOLES, time(10, 0), time(10, 45))
        
        db.session.add_all([horario1, horario2])
        db.session.commit()
        
        clase1 = Clase(
            "Spinning Intenso",
            "Clase de spinning de alta intensidad",
            20,
            entrenador1,
            horario1
        )
        clase2 = Clase(
            "Yoga Matutino",
            "Sesión de yoga relajante",
            15,
            entrenador2,
            horario2
        )
        
        clase1.planes.append(plan_premium)
        clase2.planes.extend([plan_basico, plan_premium])
        
        db.session.add_all([clase1, clase2])
        db.session.commit()
        logger.info("Clases creadas")
        
        # Crear socio de ejemplo
        socio = Socio(
            "Juan",
            "Pérez",
            "12345678",
            "juan.perez@example.com",
            plan_premium
        )
        
        db.session.add(socio)
        db.session.commit()
        logger.info("Socio de ejemplo creado")
        
        logger.info("Base de datos inicializada correctamente con datos de ejemplo")


if __name__ == '__main__':
    import sys
    
    # Verificar si se solicita inicialización de BD
    if len(sys.argv) > 1 and sys.argv[1] == 'init-db':
        logger.info("Ejecutando inicialización de base de datos...")
        init_database()
        logger.info("Inicialización completada")
        sys.exit(0)
    
    # Ejecutar aplicación
    logger.info(f"Iniciando servidor en {settings.app.host}:{settings.app.port}")
    app = create_app()
    app.run(
        debug=settings.app.debug,
        host=settings.app.host,
        port=settings.app.port
    )
