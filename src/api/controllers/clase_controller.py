"""Controlador REST para Clases"""
from flask import Blueprint, request, jsonify
from src.services.clase_service import ClaseService
from src.services.lista_espera_service import ListaEsperaService
from src.api.controllers.base_controller import handle_errors, validate_json
from src.core.logging_config import get_logger
from src.utils.enums import DiaSemana
from src.repositories.base_repository import BaseRepository
from src.models.entrenador import Entrenador
from src.models.horario import Horario

logger = get_logger(__name__)

clase_bp = Blueprint('clases', __name__, url_prefix='/api/clases')
clase_service = ClaseService()
lista_espera_service = ListaEsperaService()


@clase_bp.route('', methods=['GET'])
@handle_errors
def listar_clases():
    """
    Lista todas las clases activas.
    
    Query params:
        dia: Filtrar por día de la semana (lunes, martes, etc.)
        con_cupo: true/false - solo clases con cupo disponible
    
    Returns:
        200: Lista de clases
    """
    dia = request.args.get('dia')
    solo_con_cupo = request.args.get('con_cupo', 'false').lower() == 'true'
    
    # Filtrar por día si se especifica
    if dia:
        try:
            dia_enum = DiaSemana(dia.lower())
            clases = clase_service.listar_clases_por_dia(dia_enum)
        except ValueError:
            return jsonify({
                'success': False,
                'message': f"Día inválido: {dia}. Use: lunes, martes, miercoles, jueves, viernes, sabado, domingo"
            }), 400
    else:
        clases = clase_service.listar_clases_activas()
    
    # Filtrar por cupo si se solicita
    if solo_con_cupo:
        clases = [c for c in clases if c.tiene_cupo_disponible()]
    
    return jsonify({
        'success': True,
        'count': len(clases),
        'data': [
            {
                'id': c.id,
                'titulo': c.titulo,
                'descripcion': c.descripcion,
                'entrenador': c.entrenador.nombre_completo,
                'dia': c.horario.dia_semana.value,
                'hora_inicio': c.horario.hora_inicio,
                'duracion': c.horario.duracion_minutos,
                'cupo_maximo': c.cupo_maximo,
                'cupos_disponibles': c.cupos_disponibles(),
                'tiene_cupo': c.tiene_cupo_disponible()
            }
            for c in clases
        ]
    }), 200


@clase_bp.route('/plan/<int:plan_id>', methods=['GET'])
@handle_errors
def listar_clases_por_plan(plan_id: int):
    """
    Lista clases disponibles para un plan específico.
    
    Args:
        plan_id: ID del plan de membresía
    
    Returns:
        200: Lista de clases del plan
    """
    clases = clase_service.listar_clases_por_plan(plan_id)
    
    return jsonify({
        'success': True,
        'count': len(clases),
        'data': [
            {
                'id': c.id,
                'titulo': c.titulo,
                'descripcion': c.descripcion,
                'dia': c.horario.dia_semana.value,
                'hora_inicio': c.horario.hora_inicio
            }
            for c in clases
        ]
    }), 200


@clase_bp.route('/<int:clase_id>', methods=['GET'])
@handle_errors
def obtener_clase(clase_id: int):
    """
    Obtiene información detallada de una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Información de la clase
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': clase.id,
            'titulo': clase.titulo,
            'descripcion': clase.descripcion,
            'activa': clase.activa,
            'entrenador': {
                'id': clase.entrenador.id,
                'nombre': clase.entrenador.nombre_completo,
                'especialidad': clase.entrenador.especialidad
            },
            'horario': {
                'dia': clase.horario.dia_semana.value,
                'hora_inicio': clase.horario.hora_inicio,
                'duracion_minutos': clase.horario.duracion_minutos
            },
            'cupos': {
                'maximo': clase.cupo_maximo,
                'disponibles': clase.cupos_disponibles(),
                'ocupados': clase.cupo_maximo - clase.cupos_disponibles()
            }
        }
    }), 200


@clase_bp.route('', methods=['POST'])
@handle_errors
@validate_json('titulo', 'descripcion', 'cupo_maximo', 'entrenador_id', 'horario_id')
def crear_clase():
    """
    Crea una nueva clase.
    
    Body JSON:
        titulo: Nombre de la clase
        descripcion: Descripción de la actividad
        cupo_maximo: Cantidad máxima de participantes
        entrenador_id: ID del entrenador
        horario_id: ID del horario
        tiene_lista_espera: (opcional) Habilitar lista de espera
    
    Returns:
        201: Clase creada
        400: Datos inválidos
        404: Entrenador u horario no encontrado
    """
    data = request.get_json()
    
    # Buscar entrenador y horario
    entrenador_repo = BaseRepository(Entrenador)
    horario_repo = BaseRepository(Horario)
    
    entrenador = entrenador_repo.get_by_id(data['entrenador_id'])
    if not entrenador:
        return jsonify({
            'success': False,
            'message': f"Entrenador con ID {data['entrenador_id']} no encontrado"
        }), 404
    
    horario = horario_repo.get_by_id(data['horario_id'])
    if not horario:
        return jsonify({
            'success': False,
            'message': f"Horario con ID {data['horario_id']} no encontrado"
        }), 404
    
    # Crear clase
    clase = clase_service.crear_clase(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        cupo_maximo=data['cupo_maximo'],
        entrenador=entrenador,
        horario=horario
    )
    
    # Habilitar lista de espera si se solicita
    if data.get('tiene_lista_espera', False):
        lista_espera_service.habilitar_lista_espera(clase)
    
    logger.info(f"Clase creada: {clase.id} - {clase.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Clase creada exitosamente',
        'data': {
            'id': clase.id,
            'titulo': clase.titulo,
            'descripcion': clase.descripcion,
            'cupo_maximo': clase.cupo_maximo,
            'tiene_lista_espera': clase.tiene_lista_espera
        }
    }), 201


@clase_bp.route('/<int:clase_id>', methods=['PUT'])
@handle_errors
def actualizar_clase(clase_id: int):
    """
    Actualiza una clase existente.
    
    Args:
        clase_id: ID de la clase
    
    Body JSON (todos opcionales):
        titulo: Nuevo nombre
        descripcion: Nueva descripción
        cupo_maximo: Nuevo cupo máximo
        entrenador_id: Nuevo entrenador
        horario_id: Nuevo horario
        activa: Estado de la clase
    
    Returns:
        200: Clase actualizada
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    data = request.get_json()
    
    # Actualizar campos si están presentes
    if 'titulo' in data:
        clase.titulo = data['titulo']
    if 'descripcion' in data:
        clase.descripcion = data['descripcion']
    if 'cupo_maximo' in data:
        if data['cupo_maximo'] <= 0:
            return jsonify({
                'success': False,
                'message': 'El cupo máximo debe ser mayor a 0'
            }), 400
        clase.cupo_maximo = data['cupo_maximo']
    
    if 'entrenador_id' in data:
        entrenador_repo = BaseRepository(Entrenador)
        entrenador = entrenador_repo.get_by_id(data['entrenador_id'])
        if not entrenador:
            return jsonify({
                'success': False,
                'message': f"Entrenador con ID {data['entrenador_id']} no encontrado"
            }), 404
        clase.entrenador = entrenador
    
    if 'horario_id' in data:
        horario_repo = BaseRepository(Horario)
        horario = horario_repo.get_by_id(data['horario_id'])
        if not horario:
            return jsonify({
                'success': False,
                'message': f"Horario con ID {data['horario_id']} no encontrado"
            }), 404
        clase.horario = horario
    
    if 'activa' in data:
        clase.activa = bool(data['activa'])
    
    from src.config.database import db
    db.session.commit()
    
    logger.info(f"Clase actualizada: {clase.id} - {clase.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Clase actualizada exitosamente',
        'data': {
            'id': clase.id,
            'titulo': clase.titulo,
            'descripcion': clase.descripcion,
            'cupo_maximo': clase.cupo_maximo,
            'activa': clase.activa
        }
    }), 200


@clase_bp.route('/<int:clase_id>', methods=['DELETE'])
@handle_errors
def eliminar_clase(clase_id: int):
    """
    Elimina (desactiva) una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Clase eliminada
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    clase.desactivar()
    from src.config.database import db
    db.session.commit()
    
    logger.info(f"Clase desactivada: {clase.id} - {clase.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Clase eliminada exitosamente'
    }), 200


@clase_bp.route('/<int:clase_id>/lista-espera', methods=['POST'])
@handle_errors
def habilitar_lista_espera(clase_id: int):
    """
    Habilita la lista de espera para una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Lista de espera habilitada
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    lista_espera_service.habilitar_lista_espera(clase)
    
    return jsonify({
        'success': True,
        'message': 'Lista de espera habilitada para la clase'
    }), 200


@clase_bp.route('/<int:clase_id>/lista-espera', methods=['DELETE'])
@handle_errors
def deshabilitar_lista_espera(clase_id: int):
    """
    Deshabilita la lista de espera para una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Lista de espera deshabilitada
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    lista_espera_service.deshabilitar_lista_espera(clase)
    
    return jsonify({
        'success': True,
        'message': 'Lista de espera deshabilitada para la clase'
    }), 200


@clase_bp.route('/<int:clase_id>/lista-espera', methods=['GET'])
@handle_errors
def obtener_lista_espera(clase_id: int):
    """
    Obtiene la lista de espera de una clase.
    
    Args:
        clase_id: ID de la clase
    
    Returns:
        200: Lista de espera
        404: Clase no encontrada
    """
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    lista = lista_espera_service.obtener_lista_espera_clase(clase_id)
    
    return jsonify({
        'success': True,
        'count': len(lista),
        'data': [
            {
                'id': entrada.id,
                'socio': {
                    'id': entrada.socio.id,
                    'nombre': entrada.socio.nombre_completo,
                    'email': entrada.socio.email
                },
                'posicion': entrada.posicion,
                'fecha_inscripcion': entrada.fecha_inscripcion.isoformat(),
                'notificado': entrada.notificado,
                'confirmado': entrada.confirmado,
                'activo': entrada.activo
            }
            for entrada in lista
        ]
    }), 200

