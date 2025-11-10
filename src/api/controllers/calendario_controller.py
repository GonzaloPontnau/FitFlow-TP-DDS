"""Controlador REST para Calendario Consolidado"""
from flask import Blueprint, request, jsonify
from datetime import date
from src.services.agregador_horarios_service import (
    AgregadorHorariosService,
    ModoVisualizacion
)
from src.api.controllers.base_controller import handle_errors
from src.core.logging_config import get_logger

logger = get_logger(__name__)

calendario_bp = Blueprint('calendario', __name__, url_prefix='/api/calendario')
agregador_service = AgregadorHorariosService()


@calendario_bp.route('', methods=['GET'])
@handle_errors
def obtener_calendario():
    """
    Obtiene el calendario consolidado de todas las fuentes.
    
    Query params:
        modo: 'normal' (solo con cupo) o 'ocupado' (todas las clases)
        fecha_desde: Fecha inicial en formato YYYY-MM-DD
        fecha_hasta: Fecha final en formato YYYY-MM-DD
    
    Returns:
        200: Calendario consolidado
    """
    # Obtener parámetros
    modo_param = request.args.get('modo', 'normal').lower()
    fecha_desde_str = request.args.get('fecha_desde')
    fecha_hasta_str = request.args.get('fecha_hasta')
    
    # Validar y convertir modo
    try:
        modo = ModoVisualizacion(modo_param)
    except ValueError:
        return jsonify({
            'success': False,
            'message': f"Modo inválido: {modo_param}. Use 'normal' o 'ocupado'"
        }), 400
    
    # Convertir fechas si se proporcionan
    fecha_desde = None
    fecha_hasta = None
    
    if fecha_desde_str:
        try:
            fecha_desde = date.fromisoformat(fecha_desde_str)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f"Formato de fecha_desde inválido. Use YYYY-MM-DD"
            }), 400
    
    if fecha_hasta_str:
        try:
            fecha_hasta = date.fromisoformat(fecha_hasta_str)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f"Formato de fecha_hasta inválido. Use YYYY-MM-DD"
            }), 400
    
    # Obtener calendario consolidado
    eventos = agregador_service.obtener_calendario_consolidado(
        modo=modo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    
    return jsonify({
        'success': True,
        'count': len(eventos),
        'modo': modo.value,
        'filtros': {
            'fecha_desde': fecha_desde.isoformat() if fecha_desde else None,
            'fecha_hasta': fecha_hasta.isoformat() if fecha_hasta else None
        },
        'data': [evento.to_dict() for evento in eventos]
    }), 200


@calendario_bp.route('/estadisticas', methods=['GET'])
@handle_errors
def obtener_estadisticas():
    """
    Obtiene estadísticas del calendario consolidado.
    
    Returns:
        200: Estadísticas del calendario
    """
    estadisticas = agregador_service.obtener_estadisticas_calendario()
    
    return jsonify({
        'success': True,
        'data': estadisticas
    }), 200


@calendario_bp.route('/actualizar', methods=['POST'])
@handle_errors
def forzar_actualizacion():
    """
    Fuerza la actualización inmediata del calendario consolidado.
    
    Normalmente el calendario se actualiza automáticamente cada hora,
    pero este endpoint permite forzar una actualización manual.
    
    Returns:
        200: Calendario actualizado
    """
    agregador_service.actualizar_calendario()
    
    return jsonify({
        'success': True,
        'message': 'Calendario consolidado actualizado exitosamente'
    }), 200
