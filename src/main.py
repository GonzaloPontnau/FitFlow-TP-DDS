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

    # Carga automática de datos de prueba si la BD está vacía (solo si no es testing)
    if not settings.app.testing:
        with app.app_context():
            from src.models.plan_membresia import PlanMembresia
            try:
                # Verificar si hay planes (indicador de BD vacía)
                if PlanMembresia.query.count() == 0:
                    logger.info("Base de datos vacía detectada. Cargando datos de prueba...")
                    from init_data import init_database
                    # Ejecutamos la lógica de init_database pero adaptada para no recrear app
                    # Importamos las funciones necesarias de init_data
                    from src.models import Socio, Entrenador, Horario, Clase, Reserva
                    from src.utils.enums import DiaSemana
                    from datetime import time
                    from src.config.database import db
                    
                    # --- COPIA DE LOGICA DE CARGA DE DATOS ---
                    # Crear planes
                    plan_basico = PlanMembresia("Plan Básico", "Acceso a gimnasio de lunes a viernes de 6:00 a 16:00 y clases grupales básicas", 32000.0, nivel=1)
                    plan_premium = PlanMembresia("Plan Premium", "Acceso completo al gimnasio, todas las clases grupales, nutricionista y entrenador personal", 38000.0, nivel=2)
                    plan_estudiante = PlanMembresia("Plan Elite", "Acceso completo a todas las clases, entrenador personal dedicado, spa y área VIP", 42000.0, nivel=3)
                    db.session.add_all([plan_basico, plan_premium, plan_estudiante])
                    
                    # Crear entrenadores
                    entrenador1 = Entrenador("Carlos", "Rodríguez", "Instructor de Spinning certificado con 5 años de experiencia")
                    entrenador2 = Entrenador("María", "García", "Profesora de Yoga y Pilates")
                    entrenador3 = Entrenador("Juan", "Martínez", "Entrenador Personal y CrossFit")
                    entrenador4 = Entrenador("Ana", "López", "Instructora de Zumba y Baile")
                    entrenador5 = Entrenador("Pedro", "Sánchez", "Profesor de Funcional y TRX")
                    db.session.add_all([entrenador1, entrenador2, entrenador3, entrenador4, entrenador5])
                    db.session.commit()
                    
                    # Crear horarios y clases
                    horario1 = Horario(DiaSemana.LUNES, time(18, 0), time(19, 0))
                    clase1 = Clase("Spinning Intenso", "Clase de spinning de alta intensidad para quemar calorías", 20, entrenador1, horario1, imagen_url="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop", video_url="https://www.youtube.com/watch?v=oAPCPjnU1wA")
                    db.session.add(clase1)
                    db.session.flush()
                    clase1.planes = [plan_basico]

                    horario2 = Horario(DiaSemana.MIERCOLES, time(10, 0), time(10, 45))
                    clase2 = Clase("Yoga Matutino", "Sesión de yoga relajante para comenzar el día", 15, entrenador2, horario2, imagen_url="https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?q=80&w=1469&auto=format&fit=crop", video_url="https://www.youtube.com/watch?v=v7AYKMP6rOE")
                    db.session.add(clase2)
                    db.session.flush()
                    clase2.planes = [plan_basico]

                    horario3 = Horario(DiaSemana.MARTES, time(19, 0), time(20, 0))
                    clase3 = Clase("CrossFit Avanzado", "Entrenamiento funcional de alta intensidad", 12, entrenador3, horario3, imagen_url="https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?q=80&w=1470&auto=format&fit=crop")
                    db.session.add(clase3)
                    db.session.flush()
                    clase3.planes = [plan_premium]

                    horario4 = Horario(DiaSemana.JUEVES, time(18, 30), time(19, 30))
                    clase4 = Clase("Zumba Fitness", "Baile y ejercicio cardiovascular al ritmo de música latina", 25, entrenador4, horario4, imagen_url="https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1470&auto=format&fit=crop")
                    db.session.add(clase4)
                    db.session.flush()
                    clase4.planes = [plan_basico]

                    horario5 = Horario(DiaSemana.VIERNES, time(17, 0), time(18, 0))
                    clase5 = Clase("Funcional TRX", "Entrenamiento funcional con bandas de suspensión", 15, entrenador5, horario5, imagen_url="https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=1470&auto=format&fit=crop")
                    db.session.add(clase5)
                    db.session.flush()
                    clase5.planes = [plan_basico]

                    horario6 = Horario(DiaSemana.LUNES, time(9, 0), time(10, 0))
                    clase6 = Clase("Pilates", "Fortalecimiento del core y mejora de la postura", 18, entrenador2, horario6, imagen_url="https://images.unsplash.com/photo-1518609878373-06d740f60d8b?q=80&w=1470&auto=format&fit=crop")
                    db.session.add(clase6)
                    db.session.flush()
                    clase6.planes = [plan_basico]

                    horario7 = Horario(DiaSemana.SABADO, time(11, 0), time(12, 0))
                    clase7 = Clase("Spinning VIP Weekend", "Clase exclusiva de spinning con instructor personalizado", 10, entrenador1, horario7, imagen_url="https://images.unsplash.com/photo-1594737625785-a6cbdabd333c?q=80&w=1470&auto=format&fit=crop")
                    db.session.add(clase7)
                    db.session.flush()
                    clase7.planes = [plan_estudiante]

                    db.session.commit()
                    
                    # Crear socios
                    socio1 = Socio("Juan", "Pérez", "12345678", "juan.perez@example.com", plan_premium)
                    socio2 = Socio("María", "González", "23456789", "maria.gonzalez@example.com", plan_basico)
                    socio3 = Socio("Carlos", "Fernández", "34567890", "carlos.fernandez@example.com", plan_premium)
                    socio4 = Socio("Ana", "Martínez", "45678901", "ana.martinez@example.com", plan_estudiante)
                    socio5 = Socio("Luis", "Rodríguez", "56789012", "luis.rodriguez@example.com", plan_basico)
                    socio6 = Socio("Laura", "López", "67890123", "laura.lopez@example.com", plan_premium)
                    socio7 = Socio("Diego", "Sánchez", "78901234", "diego.sanchez@example.com", plan_estudiante)
                    socio8 = Socio("Sofía", "Ramírez", "89012345", "sofia.ramirez@example.com", plan_basico)
                    db.session.add_all([socio1, socio2, socio3, socio4, socio5, socio6, socio7, socio8])
                    db.session.commit()
                    
                    # Crear reservas
                    reserva1 = Reserva(socio1, clase1)
                    reserva2 = Reserva(socio2, clase2)
                    reserva3 = Reserva(socio3, clase3)
                    reserva4 = Reserva(socio4, clase4)
                    reserva5 = Reserva(socio1, clase2)
                    reserva6 = Reserva(socio6, clase1)
                    reserva7 = Reserva(socio6, clase3)
                    reserva8 = Reserva(socio5, clase4)
                    reserva9 = Reserva(socio7, clase2)
                    reserva10 = Reserva(socio8, clase6)
                    db.session.add_all([reserva1, reserva2, reserva3, reserva4, reserva5, reserva6, reserva7, reserva8, reserva9, reserva10])
                    db.session.commit()
                    
                    logger.info("Datos de prueba cargados exitosamente")
            except Exception as e:
                logger.error(f"Error cargando datos de prueba: {e}")

            # Actualizar imágenes faltantes en clases existentes
            try:
                from src.models.clase import Clase
                from src.config.database import db
                clases_updates = {
                    "Spinning Intenso": {
                        "imagen_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1470&auto=format&fit=crop",
                        "video_url": "https://www.youtube.com/watch?v=oAPCPjnU1wA"
                    },
                    "Yoga Matutino": {
                        "imagen_url": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?q=80&w=1469&auto=format&fit=crop",
                        "video_url": "https://www.youtube.com/watch?v=v7AYKMP6rOE"
                    },
                    "CrossFit Avanzado": {
                        "imagen_url": "https://images.unsplash.com/photo-1534367507873-d2d7e24c797f?q=80&w=1470&auto=format&fit=crop"
                    },
                    "Zumba Fitness": {
                        "imagen_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1470&auto=format&fit=crop"
                    },
                    "Funcional TRX": {
                        "imagen_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?q=80&w=1470&auto=format&fit=crop"
                    },
                    "Pilates": {
                        "imagen_url": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?q=80&w=1470&auto=format&fit=crop"
                    },
                    "Spinning VIP Weekend": {
                        "imagen_url": "https://images.unsplash.com/photo-1594737625785-a6cbdabd333c?q=80&w=1470&auto=format&fit=crop"
                    }
                }
                
                for titulo, data in clases_updates.items():
                    clase = Clase.query.filter_by(titulo=titulo).first()
                    if clase:
                        changed = False
                        if not clase.imagen_url and "imagen_url" in data:
                            clase.imagen_url = data["imagen_url"]
                            changed = True
                        if not clase.video_url and "video_url" in data:
                            clase.video_url = data["video_url"]
                            changed = True
                        
                        if changed:
                            db.session.add(clase)
                            logger.info(f"Actualizada imagen/video para clase: {titulo}")
                
                if db.session.dirty:
                    db.session.commit()
            except Exception as e:
                logger.error(f"Error actualizando imágenes de clases: {e}")
    
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
        """Cerrar sesión"""
        # Limpiar sesión completa
        session.clear()
        logger.info(f"Sesión cerrada")
        return redirect(url_for('index'))
    
    # Context Processor para inyectar usuario actual en todos los templates
    @app.context_processor
    def inject_user():
        user = None
        if session.get('admin_logged_in'):
            user = {
                'is_admin': True, 
                'name': session.get('admin_username', 'Admin'),
                'plan': None
            }
        elif session.get('socio_id'):
            # Obtener información del plan del socio
            plan_info = None
            try:
                from src.models.socio import Socio
                socio = Socio.query.get(session.get('socio_id'))
                if socio and socio.plan_membresia:
                    plan_info = {
                        'id': socio.plan_membresia.id,
                        'titulo': socio.plan_membresia.titulo,
                        'nivel': socio.plan_membresia.nivel
                    }
            except Exception:
                pass
            
            user = {
                'is_admin': False,
                'id': session.get('socio_id'),
                'name': session.get('socio_name', 'Socio'),
                'plan': plan_info
            }
        return dict(current_user=user)

    @app.route('/login-socio', methods=['POST'])
    def login_socio():
        """Login para socios mediante DNI o Email"""
        identifier = request.form.get('identifier')
        
        if not identifier:
             return render_template('login.html', error_socio='Ingrese DNI o Email', active_tab='socio')
        
        from src.models.socio import Socio
        # Buscar por DNI o Email
        socio = Socio.query.filter((Socio.dni == identifier) | (Socio.email == identifier)).first()
        
        if socio:
            session['socio_logged_in'] = True
            session['socio_id'] = socio.id
            session['socio_name'] = socio.nombre + " " + socio.apellido
            logger.info(f"Socio {socio.id} ({socio.nombre_completo}) inició sesión")
            return redirect(url_for('clases_page'))
        else:
            logger.warning(f"Intento de login socio fallido: {identifier}")
            return render_template('login.html', error_socio='Socio no encontrado', active_tab='socio')
    
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
            "Acceso a gimnasio de lunes a viernes de 6:00 a 16:00 y clases grupales básicas",
            32000.0,
            nivel=1
        )
        plan_premium = PlanMembresia(
            "Plan Premium",
            "Acceso completo al gimnasio, todas las clases grupales, nutricionista y entrenador personal",
            38000.0,
            nivel=2
        )
        plan_estudiante = PlanMembresia(
            "Plan Elite",
            "Acceso completo a todas las clases, entrenador personal dedicado, spa y área VIP",
            42000.0,
            nivel=3
        )
        
        db.session.add_all([plan_basico, plan_premium, plan_estudiante])
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
