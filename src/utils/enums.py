"""Enumeraciones y constantes del sistema"""
from enum import Enum


class RolUsuario(Enum):
    """Roles de usuario en el sistema"""
    ADMINISTRADOR = "administrador"
    SOCIO_REGISTRADO = "socio_registrado"
    VISUALIZADOR = "visualizador"


class EstadoSolicitudBaja(Enum):
    """Estados posibles de una solicitud de baja"""
    PENDIENTE = "pendiente"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


class DiaSemana(Enum):
    """Días de la semana"""
    LUNES = "lunes"
    MARTES = "martes"
    MIERCOLES = "miercoles"
    JUEVES = "jueves"
    VIERNES = "viernes"
    SABADO = "sabado"
    DOMINGO = "domingo"


class EstadoMembresia(Enum):
    """Estados de la membresía de un socio"""
    ACTIVA = "activa"
    VENCIDA = "vencida"
    SUSPENDIDA = "suspendida"
    BAJA_SOLICITADA = "baja_solicitada"
    BAJA_DEFINITIVA = "baja_definitiva"


# Constantes
LONGITUD_MINIMA_SOLICITUD_BAJA = 150
HORARIO_CANCELACION_RESERVA_HORAS = 24
