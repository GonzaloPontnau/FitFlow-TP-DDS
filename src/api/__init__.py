"""API REST del sistema FitFlow"""
from .controllers import (
    socio_bp,
    clase_bp,
    reserva_bp,
    pago_bp
)

__all__ = [
    'socio_bp',
    'clase_bp',
    'reserva_bp',
    'pago_bp'
]

