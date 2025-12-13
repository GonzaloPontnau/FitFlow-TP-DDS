"""Controlador REST para Socios"""
from flask import Blueprint, request, jsonify
from src.repositories.socio_repository import SocioRepository
from src.services.socio_service import SocioService
from src.api.controllers.base_controller import handle_errors, paginate
from src.core.logging_config import get_logger
from src.exceptions.base_exceptions import NotFoundException

logger = get_logger(__name__)

socio_bp = Blueprint('socios', __name__, url_prefix='/api/socios')
socio_repository = SocioRepository()
socio_service = SocioService()


@socio_bp.route('', methods=['GET'])
@handle_errors
@paginate(default_page_size=20)
def listar_socios(page: int, page_size: int):
    """
    Lista todos los socios (paginado).
    
    Query params:
        page: Número de página (default: 1)
        page_size: Tamaño de página (default: 20, max: 100)
        estado: Filtrar por estado de membresía
    
    Returns:
        200: Lista de socios
    """
    # TODO: Implementar paginación en repository
    socios = socio_repository.get_all()
    
    # Filtrar por estado si se especifica
    estado_filtro = request.args.get('estado')
    if estado_filtro:
        from src.utils.enums import EstadoMembresia
        try:
            estado_enum = EstadoMembresia(estado_filtro)
            socios = [s for s in socios if s.estado_membresia == estado_enum]
        except ValueError:
            pass  # Ignorar filtro inválido
    
    return jsonify({
        'success': True,
        'count': len(socios),
        'data': [
            {
                'id': s.id,
                'nombre_completo': s.nombre_completo,
                'dni': s.dni,
                'email': s.email,
                'estado_membresia': s.estado_membresia.value,
                'plan': s.plan_membresia.titulo if s.plan_membresia else None
            }
            for s in socios
        ]
    }), 200


@socio_bp.route('/<int:socio_id>', methods=['GET'])
@handle_errors
def obtener_socio(socio_id: int):
    """
    Obtiene información detallada de un socio.
    
    Args:
        socio_id: ID del socio
    
    Returns:
        200: Información del socio
        404: Socio no encontrado
    """
    socio = socio_repository.find_by_id(socio_id)
    
    if not socio:
        raise NotFoundException('Socio', socio_id)
    
    return jsonify({
        'success': True,
        'data': {
            'id': socio.id,
            'nombre': socio.nombre,
            'apellido': socio.apellido,
            'dni': socio.dni,
            'email': socio.email,
            'rol': socio.rol.value,
            'estado_membresia': socio.estado_membresia.value,
            'plan': {
                'id': socio.plan_membresia.id,
                'titulo': socio.plan_membresia.titulo,
                'precio': socio.plan_membresia.precio
            } if socio.plan_membresia else None
        }
    }), 200


@socio_bp.route('/<int:socio_id>/estadisticas', methods=['GET'])
@handle_errors
def obtener_estadisticas_socio(socio_id: int):
    """
    Obtiene estadísticas de un socio.
    
    Args:
        socio_id: ID del socio
    
    Returns:
        200: Estadísticas del socio
    """
    socio = socio_repository.find_by_id(socio_id)
    
    if not socio:
        raise NotFoundException('Socio', socio_id)
    
    return jsonify({
        'success': True,
        'data': {
            'total_reservas': len(socio.reservas),
            'reservas_activas': len([r for r in socio.reservas if r.esta_activa()]),
            'total_pagos': len(socio.pagos),
            'solicitudes_baja': len(socio.solicitudes_baja)
        }
    }), 200

@socio_bp.route('', methods=['POST'])
@handle_errors
def crear_socio():
    """
    Crea un nuevo socio.
    Esperamos un JSON con: nombre, apellido, dni, email, plan_id (opcional)
    """
    data = request.get_json()
    
    if not data:
        # Puedes levantar una excepción o retornar error manual
        return jsonify({'success': False, 'message': 'No se enviaron datos JSON'}), 400

    # Llamamos al SERVICIO (no al repositorio directo)
    # El servicio se encarga de validar DNI duplicado y buscar el objeto Plan
    nuevo_socio = socio_service.crear_socio(data)

    return jsonify({
        'success': True,
        'message': 'Socio creado exitosamente',
        'data': {
            'id': nuevo_socio.id,
            'nombre_completo': nuevo_socio.nombre_completo,
            'dni': nuevo_socio.dni,
            'email': nuevo_socio.email,
            'estado': nuevo_socio.estado_membresia.value,
            'plan': nuevo_socio.plan_membresia.titulo if nuevo_socio.plan_membresia else None
        }
    }), 201