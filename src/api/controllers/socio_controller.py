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
csv_importer = None # Lazy import to avoid circular dependencies if any, or just init here.
from src.services.csv_importer_service import CSVImporterService
csv_importer = CSVImporterService()


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


@socio_bp.route('/<int:socio_id>', methods=['DELETE'])
@handle_errors
def eliminar_socio(socio_id: int):
    """
    Elimina un socio del sistema.
    
    Args:
        socio_id: ID del socio a eliminar
    
    Returns:
        200: Socio eliminado exitosamente
        404: Socio no encontrado
    """
    socio = socio_repository.get_by_id(socio_id)
    
    if not socio:
        raise NotFoundException('Socio', socio_id)
    
    nombre = socio.nombre_completo
    
    # Eliminar reservas asociadas primero para evitar constraint errors
    from src.config.database import db
    for reserva in socio.reservas:
        db.session.delete(reserva)
    
    # Eliminar solicitudes de baja asociadas
    for solicitud in socio.solicitudes_baja:
        db.session.delete(solicitud)
    
    # Eliminar pagos asociados
    for pago in socio.pagos:
        db.session.delete(pago)
    
    # Ahora eliminar el socio
    db.session.delete(socio)
    db.session.commit()
    
    logger.info(f"Socio {socio_id} ({nombre}) eliminado")
    
    return jsonify({
        'success': True,
        'message': f'Socio {nombre} eliminado exitosamente'
    }), 200

@socio_bp.route('/importar-csv', methods=['POST'])
@handle_errors
def importar_csv():
    """
    Importa socios desde un archivo CSV.
    """
    if 'archivo' not in request.files:
        return jsonify({'success': False, 'message': 'No se seleccionó ningún archivo'}), 400
    
    archivo = request.files['archivo']
    
    if archivo.filename == '':
        return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
    if not archivo.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'El archivo debe ser un CSV'}), 400

    import os
    import tempfile
    
    # Guardar archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
        archivo.save(temp_file.name)
        temp_path = temp_file.name
        
    try:
        resultado = csv_importer.importar_socios(temp_path)
        
        # Eliminar archivo temporal
        os.unlink(temp_path)
        
        if resultado['errores']:
            return jsonify({
                'success': True, # Partial success potentially
                'message': f"Procesado con advertencias: {len(resultado['errores'])} errores.",
                'data': resultado
            }), 200
        else:
             return jsonify({
                'success': True,
                'message': 'Importación completada exitosamente',
                'data': resultado
            }), 200
            
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e