"""Punto de entrada principal de la aplicación FitFlow"""
from functools import wraps
from flask import Flask, jsonify, render_template, session, redirect, url_for, request
from src.config.database import init_db
from src.config.settings import settings
from src.core.logging_config import setup_logging, get_logger
from src.api.controllers import (
    socio_bp, clase_bp, reserva_bp, pago_bp, 
    plan_bp, solicitud_bp, calendario_bp, estadisticas_bp
)
from src.exceptions.base_exceptions import FitFlowException
from src.extensions import socketio, limiter

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
    # Usar UUID para que las sesiones expiren al reiniciar el servidor
    # Usar UUID para que las sesiones expiren al reiniciar el servidor
    # IMPORTANTE: Desactivado UUID dinámico porque rompe el login en waitress con múltiples workers/reinicios
    # import uuid
    # runtime_secret = f"{settings.app.secret_key}_{uuid.uuid4()}"
    app.config['SECRET_KEY'] = settings.app.secret_key
    app.config['SESSION_PERMANENT'] = False  # Sesión expira al cerrar navegador
    
    # Configuración de Cookies para Desarrollo (Localhost)
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    app.config['DEBUG'] = settings.app.debug
    app.config['TESTING'] = settings.app.testing
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.database.url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = settings.database.echo
    
    logger.info("Inicializando aplicación FitFlow...")
    print(">>> DEBUG: LOADING MAIN.PY v2 with /solicitar-baja <<<")
    
    # Inicializar extensiones
    init_db(app)
    socketio.init_app(app)
    limiter.init_app(app)
    logger.info("Extensiones inicializadas (DB, SocketIO, Limiter)")
    
    # Registrar blueprints (controladores REST)
    app.register_blueprint(socio_bp)
    app.register_blueprint(clase_bp)
    app.register_blueprint(reserva_bp)
    app.register_blueprint(pago_bp)
    app.register_blueprint(plan_bp)
    app.register_blueprint(solicitud_bp)
    app.register_blueprint(calendario_bp)
    app.register_blueprint(estadisticas_bp)
    logger.info("Controladores REST registrados")
    
    # Configurar tareas programadas (scheduler)
    scheduler_active = False
    try:
        from src.config.scheduler import configurar_tareas_programadas
        scheduler = configurar_tareas_programadas(app)
        scheduler_active = True
        logger.info("Tareas asincrónicas configuradas")
    except Exception as e:
        logger.warning(f"No se pudieron configurar tareas asincrónicas: {e}")
        logger.warning("La aplicación continuará sin scheduler")
    
    # Manejador global de errores
    @app.errorhandler(FitFlowException)
    def handle_fitflow_exception(error):
        """Maneja excepciones personalizadas del sistema"""
        logger.error(f"FitFlowException: {error.message}")
        return jsonify(error.to_dict()), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404"""
        from flask import request
        # Si es una petición a la API, devolver JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'error': {
                    'type': 'NOT_FOUND',
                    'message': 'Recurso no encontrado',
                    'details': {}
                }
            }), 404
        # Si es una petición web normal, devolver página de error
        return render_template('index.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores internos del servidor"""
        from flask import request
        logger.exception("Error interno del servidor")
        # Si es una petición a la API, devolver JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'error': {
                    'type': 'INTERNAL_ERROR',
                    'message': 'Error interno del servidor',
                    'details': {}
                }
            }), 500
        # Si es una petición web normal, devolver página de error
        return render_template('index.html'), 500
    
    # Middleware para bloqueo de IPs
    @app.before_request
    def bloquear_ips():
        """Verifica si la IP del cliente está bloqueada"""
        from flask import request, abort
        
        # Lista de IPs bloqueadas (podría venir de BD o config)
        ips_bloqueadas = settings.app.blocked_ips or []
        
        if request.remote_addr in ips_bloqueadas:
            logger.warning(f"Acceso denegado a IP bloqueada: {request.remote_addr}")
            abort(403, description="Acceso denegado: IP bloqueada")

    # Middleware para evitar caché en API
    @app.after_request
    def add_header(response):
        if request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Decorador para requerir login de admin
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('admin_logged_in'):
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Rutas Web (templates HTML)
    # ===== PAGINAS PUBLICAS (visualizacion sin login) =====
    @app.route('/')
    def index():
        """Página principal - pública"""
        return render_template('index.html')
    
    @app.route('/clases')
    def clases_page():
        """Página de clases - pública para visualización"""
        return render_template('clases.html')
    
    @app.route('/planes')
    def planes_page():
        """Página de planes de membresía - pública para visualización"""
        return render_template('planes.html')
    
    @app.route('/calendario')
    def calendario_page():
        """Página del calendario de clases - pública para visualización"""
        return render_template('calendario.html')

    @app.route('/solicitar-baja')
    def solicitar_baja_page():
        """Página pública para solicitar baja"""
        return render_template('solicitar_baja.html')
    
    # ===== PAGINAS PROTEGIDAS (requieren login de admin) =====
    @app.route('/socios')
    @admin_required
    def socios_page():
        """Página de gestión de socios - requiere login"""
        return render_template('socios.html')
    
    @app.route('/reservas')
    @admin_required
    def reservas_page():
        """Página de gestión de reservas - requiere login"""
        return render_template('reservas.html')
    
    @app.route('/admin')
    @admin_required
    def admin_page():
        """Panel de administración - requiere login"""
        return render_template('admin.html')
    
    @app.route('/estadisticas/dashboard')
    @admin_required
    def estadisticas_page():
        """Dashboard de estadísticas - requiere login"""
        return render_template('estadisticas.html')
    
    @app.route('/solicitudes')
    @admin_required
    def solicitudes_page():
        """Gestión de solicitudes de baja - requiere login"""
        return render_template('solicitudes.html')
    
    @app.route('/admin/planes')
    @admin_required
    def admin_planes_page():
        """Gestión de planes de membresía - requiere login"""
        return render_template('admin_planes.html')
    
    # Credenciales de admin (en producción usar DB o env vars)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    @app.route('/login', methods=['GET', 'POST'])
    def login_page():
        """Página de login de administrador"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            print(f">>> DEBUG LOGIN: User={username}, Pass={password}, ExpectedUser={ADMIN_USERNAME}, ExpectedPass={ADMIN_PASSWORD}")
            
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session['admin_logged_in'] = True
                session['admin_username'] = username
                logger.info(f"Admin {username} inició sesión")
                print(">>> DEBUG LOGIN: SUCCESS! Redirecting...")
                return redirect(url_for('admin_page'))
            else:
                print(f">>> DEBUG LOGIN: FAILED match. UserMatch={username==ADMIN_USERNAME}, PassMatch={password==ADMIN_PASSWORD}")
                logger.warning(f"Intento de login fallido para usuario: {username}")
                return render_template('login.html', error='Usuario o contraseña incorrectos')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """Cerrar sesión de administrador"""
        username = session.get('admin_username', 'Unknown')
        session.clear()
        logger.info(f"Admin {username} cerró sesión")
        return redirect(url_for('index'))
    
    # API Endpoints informativos
    @app.route('/api')
    @limiter.limit("10 per minute")
    def api_info():
        """Endpoint raíz con información de la API"""
        return jsonify({
            'message': 'FitFlow API - Sistema de Gestión para Gimnasios',
            'version': '3.0.0',
            'status': 'active',
            'endpoints': {
                'socios': '/api/socios',
                'clases': '/api/clases',
                'reservas': '/api/reservas',
                'pagos': '/api/pagos',
                'planes': '/api/planes',
                'solicitudes': '/api/solicitudes',
                'calendario': '/api/calendario',
                'estadisticas': '/api/estadisticas',
                'health': '/health'
            }
        })
    
    @app.route('/health')
    def health():
        """
        Endpoint para verificar el estado del servicio.
        
        Verifica:
        - Conectividad a la base de datos
        - Tiempo de respuesta
        - Uptime de la aplicación
        """
        import time
        from datetime import datetime
        
        start_time = time.time()
        health_status = {
            'status': 'healthy',
            'version': '3.0.0',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        # Verificar conectividad a la base de datos
        try:
            from src.config.database import db
            db.session.execute(db.text('SELECT 1'))
            health_status['checks']['database'] = {
                'status': 'connected',
                'type': 'sqlite'
            }
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['checks']['database'] = {
                'status': 'disconnected',
                'error': str(e)
            }
        
        # Tiempo de respuesta
        response_time_ms = (time.time() - start_time) * 1000
        health_status['response_time_ms'] = round(response_time_ms, 2)
        
        # Información del sistema
        health_status['checks']['scheduler'] = {
            'status': 'running' if scheduler_active else 'stopped'
        }
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
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
            "Rodriguez",
            "carlos.rodriguez@fitflow.com",
            "Instructor de Spinning"
        )
        entrenador2 = Entrenador(
            "Maria",
            "Garcia",
            "maria.garcia@fitflow.com",
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
            horario1,
            imagen_url="https://example.com/spinning.jpg"
        )
        clase2 = Clase(
            "Yoga Matutino",
            "Sesión de yoga relajante",
            15,
            entrenador2,
            horario2,
            video_url="https://example.com/yoga_demo.mp4"
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
    socketio.run(
        app,
        debug=settings.app.debug,
        host=settings.app.host,
        port=settings.app.port
    )
