"""Controlador REST para Solicitudes de Baja"""
from flask import Blueprint, request, jsonify
from src.services.solicitud_baja_service import SolicitudBajaService
from src.api.controllers.base_controller import handle_errors, validate_json
from src.core.logging_config import get_logger

logger = get_logger(__name__)

solicitud_bp = Blueprint('solicitudes', __name__, url_prefix='/api/solicitudes')
solicitud_service = SolicitudBajaService()


@solicitud_bp.route('', methods=['GET'])
@handle_errors
def listar_solicitudes():
    """
    Lista todas las solicitudes de baja pendientes.
    
    Returns:
        200: Lista de solicitudes pendientes
    """
    solicitudes = solicitud_service.listar_solicitudes_pendientes()
    
    return jsonify({
        'success': True,
        'count': len(solicitudes),
        'data': [
            {
                'id': sol.id,
                'socio': {
                    'id': sol.socio.id,
                    'nombre': sol.socio.nombre_completo,
                    'email': sol.socio.email,
                    'plan': sol.socio.plan_membresia.titulo if sol.socio.plan_membresia else None
                },
                'justificacion': sol.justificacion,
                'fecha_solicitud': sol.fecha_solicitud.isoformat(),
                'estado': sol.estado.value
            }
            for sol in solicitudes
        ]
    }), 200


@solicitud_bp.route('/<int:solicitud_id>', methods=['GET'])
@handle_errors
def obtener_solicitud(solicitud_id: int):
    """
    Obtiene información detallada de una solicitud de baja.
    
    Args:
        solicitud_id: ID de la solicitud
    
    Returns:
        200: Información de la solicitud
        404: Solicitud no encontrada
    """
    try:
        solicitud = solicitud_service.obtener_solicitud(solicitud_id)
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': solicitud.id,
            'socio': {
                'id': solicitud.socio.id,
                'nombre': solicitud.socio.nombre_completo,
                'email': solicitud.socio.email,
                'dni': solicitud.socio.dni,
                'plan': solicitud.socio.plan_membresia.titulo if solicitud.socio.plan_membresia else None
            },
            'justificacion': solicitud.justificacion,
            'fecha_solicitud': solicitud.fecha_solicitud.isoformat(),
            'fecha_resolucion': solicitud.fecha_resolucion.isoformat() if solicitud.fecha_resolucion else None,
            'estado': solicitud.estado.value,
            'comentario_admin': solicitud.comentario_admin
        }
    }), 200


@solicitud_bp.route('', methods=['POST'])
@handle_errors
@validate_json('socio_id', 'justificacion')
def crear_solicitud():
    """
    Crea una nueva solicitud de baja.
    
    Body JSON:
        socio_id: ID del socio que solicita la baja
        justificacion: Texto justificando la solicitud (mínimo 20 caracteres)
    
    Returns:
        201: Solicitud creada
        400: Datos inválidos o justificación insuficiente
    """
    data = request.get_json()
    
    try:
        solicitud = solicitud_service.crear_solicitud(
            socio_id=data['socio_id'],
            justificacion=data['justificacion']
        )
        
        logger.info(f"Solicitud de baja creada: {solicitud.id} (socio {data['socio_id']})")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud de baja creada exitosamente',
            'data': {
                'id': solicitud.id,
                'estado': solicitud.estado.value,
                'fecha_solicitud': solicitud.fecha_solicitud.isoformat()
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@solicitud_bp.route('/publica', methods=['POST'])
@handle_errors
@validate_json('dni', 'email', 'justificacion')
def crear_solicitud_publica():
    """
    Endpoint PÚBLICO para crear solicitud de baja.
    
    Body JSON:
        dni: DNI del socio
        email: Email del socio
        justificacion: Motivo de la baja
    
    Returns:
        201: Solicitud creada
        400: Datos inválidos
    """
    data = request.get_json()
    
    try:
        solicitud = solicitud_service.crear_solicitud_publica(
            dni=data['dni'],
            email=data['email'],
            justificacion=data['justificacion']
        )
        
        logger.info(f"Solicitud pública creada: {solicitud.id} (DNI {data['dni']})")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud enviada correctamente',
            'data': {
                'id': solicitud.id,
                'fecha_solicitud': solicitud.fecha_solicitud.isoformat()
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@solicitud_bp.route('/<int:solicitud_id>/aprobar', methods=['PUT'])
@handle_errors
def aprobar_solicitud(solicitud_id: int):
    """
    Aprueba una solicitud de baja.
    
    Args:
        solicitud_id: ID de la solicitud
    
    Body JSON (opcional):
        comentario_admin: Comentario del administrador
    
    Returns:
        200: Solicitud aprobada
        400: Error en la operación
        404: Solicitud no encontrada
    """
    data = request.get_json() or {}
    comentario = data.get('comentario_admin')
    
    try:
        solicitud = solicitud_service.aprobar_solicitud(
            solicitud_id=solicitud_id,
            comentario_admin=comentario
        )
        
        logger.info(f"Solicitud de baja aprobada: {solicitud_id}")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud aprobada exitosamente',
            'data': {
                'id': solicitud.id,
                'estado': solicitud.estado.value,
                'fecha_resolucion': solicitud.fecha_resolucion.isoformat()
            }
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@solicitud_bp.route('/<int:solicitud_id>/rechazar', methods=['PUT'])
@handle_errors
@validate_json('comentario_admin')
def rechazar_solicitud(solicitud_id: int):
    """
    Rechaza una solicitud de baja.
    
    Args:
        solicitud_id: ID de la solicitud
    
    Body JSON:
        comentario_admin: Motivo del rechazo (obligatorio)
    
    Returns:
        200: Solicitud rechazada
        400: Error en la operación
        404: Solicitud no encontrada
    """
    data = request.get_json()
    
    try:
        solicitud = solicitud_service.rechazar_solicitud(
            solicitud_id=solicitud_id,
            comentario_admin=data['comentario_admin']
        )
        
        logger.info(f"Solicitud de baja rechazada: {solicitud_id}")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud rechazada exitosamente',
            'data': {
                'id': solicitud.id,
                'estado': solicitud.estado.value,
                'fecha_resolucion': solicitud.fecha_resolucion.isoformat(),
                'comentario_admin': solicitud.comentario_admin
            }
        }), 200
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400


@solicitud_bp.route('/socio/<int:socio_id>', methods=['GET'])
@handle_errors
def obtener_solicitudes_socio(socio_id: int):
    """
    Obtiene todas las solicitudes de un socio específico.
    
    Args:
        socio_id: ID del socio
    
    Returns:
        200: Lista de solicitudes del socio
    """
    solicitudes = solicitud_service.obtener_solicitudes_socio(socio_id)
    
    return jsonify({
        'success': True,
        'count': len(solicitudes),
        'data': [
            {
                'id': sol.id,
                'justificacion': sol.justificacion,
                'fecha_solicitud': sol.fecha_solicitud.isoformat(),
                'fecha_resolucion': sol.fecha_resolucion.isoformat() if sol.fecha_resolucion else None,
                'estado': sol.estado.value,
                'comentario_admin': sol.comentario_admin
            }
            for sol in solicitudes
        ]
    }), 200
