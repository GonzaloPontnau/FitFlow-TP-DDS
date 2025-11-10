"""Excepciones base del sistema"""


class FitFlowException(Exception):
    """
    Excepción base para todas las excepciones del sistema FitFlow.
    
    Todas las excepciones personalizadas deben heredar de esta clase.
    """
    def __init__(self, message: str, code: str = None, details: dict = None):
        """
        Args:
            message: Mensaje descriptivo del error
            code: Código único del error (ej: "SOCIO_NOT_FOUND")
            details: Detalles adicionales del error
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convierte la excepción a un diccionario para respuestas API"""
        return {
            'error': {
                'type': self.code,
                'message': self.message,
                'details': self.details
            }
        }


class ValidationException(FitFlowException):
    """
    Excepción para errores de validación de datos.
    
    Se lanza cuando los datos de entrada no cumplen con las reglas de validación.
    """
    def __init__(self, message: str, field: str = None, value: any = None):
        super().__init__(
            message=message,
            code='VALIDATION_ERROR',
            details={'field': field, 'value': str(value) if value else None}
        )


class NotFoundException(FitFlowException):
    """
    Excepción para entidades no encontradas.
    
    Se lanza cuando se intenta acceder a una entidad que no existe.
    """
    def __init__(self, entity: str, identifier: any):
        super().__init__(
            message=f"{entity} con identificador '{identifier}' no encontrado",
            code='NOT_FOUND',
            details={'entity': entity, 'identifier': str(identifier)}
        )


class BusinessRuleException(FitFlowException):
    """
    Excepción para violaciones de reglas de negocio.
    
    Se lanza cuando una operación viola una regla de negocio del dominio.
    """
    def __init__(self, message: str, rule: str = None):
        super().__init__(
            message=message,
            code='BUSINESS_RULE_VIOLATION',
            details={'rule': rule}
        )


# Alias para compatibilidad
BusinessException = BusinessRuleException


class ExternalServiceException(FitFlowException):
    """
    Excepción para errores en servicios externos.
    
    Se lanza cuando falla la comunicación con un servicio externo (proxy).
    """
    def __init__(self, service: str, message: str, original_error: Exception = None):
        super().__init__(
            message=f"Error en servicio externo '{service}': {message}",
            code='EXTERNAL_SERVICE_ERROR',
            details={
                'service': service,
                'original_error': str(original_error) if original_error else None
            }
        )


class ConflictException(FitFlowException):
    """
    Excepción para conflictos de estado.
    
    Se lanza cuando hay un conflicto con el estado actual del sistema.
    """
    def __init__(self, message: str, resource: str = None):
        super().__init__(
            message=message,
            code='CONFLICT',
            details={'resource': resource}
        )


class UnauthorizedException(FitFlowException):
    """
    Excepción para acceso no autorizado.
    
    Se lanza cuando un usuario intenta realizar una acción sin permisos.
    """
    def __init__(self, message: str = "No autorizado", action: str = None):
        super().__init__(
            message=message,
            code='UNAUTHORIZED',
            details={'action': action}
        )

