"""Controladores REST de la API"""
from .socio_controller import socio_bp
from .clase_controller import clase_bp
from .reserva_controller import reserva_bp
from .pago_controller import pago_bp
from .plan_controller import plan_bp
from .solicitud_baja_controller import solicitud_bp
from .calendario_controller import calendario_bp
from .estadisticas_controller import estadisticas_bp

__all__ = [
    'socio_bp',
    'clase_bp',
    'reserva_bp',
    'pago_bp',
    'plan_bp',
    'solicitud_bp',
    'calendario_bp',
    'estadisticas_bp'
]

