from flask import Blueprint, request, jsonify
from src.services.reserva_service import ReservaService
from src.services.lista_espera_service import ListaEsperaService
from src.api.controllers.base_controller import handle_errors, validate_json
from src.core.logging_config import get_logger
from src.exceptions.base_exceptions import ValidationException

logger = get_logger(__name__)

reserva_bp = Blueprint('reservas', __name__, url_prefix='/api/reservas')
reserva_service = ReservaService()
lista_espera_service = ListaEsperaService()


@reserva_bp.route('/espera', methods=['POST'])
@handle_errors
@validate_json('socio_id', 'clase_id')
def unirse_lista_espera():
    """
    Une a un socio a la lista de espera de una clase.
    """
    data = request.get_json()
    socio_id = data['socio_id']
    clase_id = data['clase_id']

    from src.repositories.base_repository import BaseRepository
    from src.models.socio import Socio
    from src.models.clase import Clase

    socio = BaseRepository(Socio).get_by_id(socio_id)
    clase = BaseRepository(Clase).get_by_id(clase_id)

    if not socio or not clase:
         return jsonify({'success': False, 'message': 'Socio o Clase no encontrados'}), 404

    try:
        entrada = lista_espera_service.inscribir_en_lista_espera(socio, clase)
        return jsonify({
            'success': True, 
            'message': f'Inscrito en lista de espera. Posición: {entrada.posicion}',
            'data': {'posicion': entrada.posicion}
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400


@reserva_bp.route('', methods=['GET'])
@handle_errors
def listar_reservas():
    """
    Lista todas las reservas del sistema.
    
    Query params:
        activas: true/false (default: all)
    
    Returns:
        200: Lista de reservas
    """
    solo_activas = request.args.get('activas', '').lower() == 'true'
    
    # Obtener todas las reservas
    from src.repositories.base_repository import BaseRepository
    from src.models.reserva import Reserva
    
    repo = BaseRepository(Reserva)
    reservas = repo.get_all()
    
    # Filtrar por activas si se solicita
    if solo_activas:
        reservas = [r for r in reservas if r.esta_activa()]
    
    return jsonify({
        'success': True,
        'count': len(reservas),
        'data': [
            {
                'id': r.id,
                'socio_id': r.socio_id,
                'socio_nombre': r.socio.nombre_completo,
                'clase_id': r.clase_id,
                'clase_titulo': r.clase.titulo,
                'fecha_reserva': r.fecha_reserva.isoformat(),
                'confirmada': r.confirmada,
                'fecha_cancelacion': r.fecha_cancelacion.isoformat() if r.fecha_cancelacion else None
            }
            for r in reservas
        ]
    }), 200


@reserva_bp.route('', methods=['POST'])
@handle_errors
@validate_json('socio_id', 'clase_id')
def crear_reserva():
    """
    Crea una nueva reserva.
    
    Body JSON:
        {
            "socio_id": 1,
            "clase_id": 5
        }
    
    Returns:
        201: Reserva creada exitosamente
        400: Error de validación o regla de negocio
    """
    data = request.get_json()
    
    socio_id = data['socio_id']
    clase_id = data['clase_id']
    
    resultado = reserva_service.crear_reserva(socio_id, clase_id)
    
    if resultado['success']:
        logger.info(f"Reserva creada: Socio {socio_id} - Clase {clase_id}")
        return jsonify({
            'success': True,
            'message': resultado['message'],
            'data': {
                'reserva_id': resultado['reserva'].id if resultado['reserva'] else None
            }
        }), 201
    else:
        logger.warning(f"Fallo al crear reserva: {resultado['message']}")
        return jsonify({
            'success': False,
            'message': resultado['message']
        }), 400


@reserva_bp.route('/<int:reserva_id>', methods=['DELETE'])
@handle_errors
def cancelar_reserva(reserva_id: int):
    """
    Cancela una reserva existente.
    
    Args:
        reserva_id: ID de la reserva a cancelar
    
    Returns:
        200: Reserva cancelada exitosamente
        400: Error al cancelar
        404: Reserva no encontrada
    """
    resultado = reserva_service.cancelar_reserva(reserva_id)
    
    if resultado['success']:
        logger.info(f"Reserva {reserva_id} cancelada")
        return jsonify({
            'success': True,
            'message': resultado['message']
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': resultado['message']
        }), 400


@reserva_bp.route('/socio/<int:socio_id>', methods=['GET'])
@handle_errors
def listar_reservas_socio(socio_id: int):
    """
    Lista las reservas activas de un socio.
    
    Args:
        socio_id: ID del socio
    
    Query params:
        activas: true/false (default: true)
    
    Returns:
        200: Lista de reservas
    """
    solo_activas = request.args.get('activas', 'true').lower() == 'true'
    
    if solo_activas:
        reservas = reserva_service.listar_reservas_activas_socio(socio_id)
    else:
        reservas = reserva_service.listar_reservas_socio(socio_id)
    
    return jsonify({
        'success': True,
        'count': len(reservas),
        'data': [
            {
                'id': r.id,
                'clase_id': r.clase_id,
                'clase_titulo': r.clase.titulo,
                'fecha_reserva': r.fecha_reserva.isoformat(),
                'confirmada': r.confirmada
            }
            for r in reservas
        ]
    }), 200


@reserva_bp.route('/clase/<int:clase_id>/cupos', methods=['GET'])
@handle_errors
def consultar_cupos(clase_id: int):
    """
    Consulta información de cupos de una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Información de cupos
    """
    info_cupos = reserva_service.get_cupos_disponibles(clase_id)
    
    return jsonify({
        'success': True,
        'data': info_cupos
    }), 200

