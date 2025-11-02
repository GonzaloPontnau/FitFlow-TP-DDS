"""Controladores REST de la API"""
from .socio_controller import socio_bp
from .clase_controller import clase_bp
from .reserva_controller import reserva_bp
from .pago_controller import pago_bp

__all__ = [
    'socio_bp',
    'clase_bp',
    'reserva_bp',
    'pago_bp'
]

