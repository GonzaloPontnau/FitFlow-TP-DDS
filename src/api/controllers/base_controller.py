"""Controlador base con funcionalidad común"""
from flask import jsonify, request
from functools import wraps
from src.exceptions.base_exceptions import FitFlowException, ValidationException
from src.core.logging_config import get_logger

logger = get_logger(__name__)


def handle_errors(f):
    """
    Decorator para manejo centralizado de errores en endpoints.
    
    Captura excepciones y retorna respuestas HTTP apropiadas.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationException as e:
            logger.warning(f"Error de validación: {e.message}")
            return jsonify(e.to_dict()), 400
        except FitFlowException as e:
            logger.error(f"Error de negocio: {e.message}")
            return jsonify(e.to_dict()), 400
        except Exception as e:
            logger.exception(f"Error inesperado: {str(e)}")
            return jsonify({
                'error': {
                    'type': 'INTERNAL_ERROR',
                    'message': 'Error interno del servidor',
                    'details': {}
                }
            }), 500
    return decorated_function


def validate_json(*required_fields):
    """
    Decorator para validar campos requeridos en el body JSON.
    
    Args:
        required_fields: Campos que deben estar presentes en el JSON
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                raise ValidationException(
                    "Content-Type debe ser application/json",
                    field="Content-Type"
                )
            
            data = request.get_json()
            missing_fields = [
                field for field in required_fields 
                if field not in data or data[field] is None
            ]
            
            if missing_fields:
                raise ValidationException(
                    f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                    field=missing_fields[0]
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def paginate(default_page_size=20, max_page_size=100):
    """
    Decorator para añadir paginación a los endpoints.
    
    Extrae parámetros page y page_size del query string.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                page = int(request.args.get('page', 1))
                page_size = int(request.args.get('page_size', default_page_size))
                
                if page < 1:
                    page = 1
                if page_size < 1 or page_size > max_page_size:
                    page_size = default_page_size
                
                kwargs['page'] = page
                kwargs['page_size'] = page_size
                
            except ValueError:
                raise ValidationException(
                    "page y page_size deben ser números enteros",
                    field="pagination"
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

