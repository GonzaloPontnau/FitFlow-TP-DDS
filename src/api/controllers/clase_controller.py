"""Controlador REST para Clases"""
from flask import Blueprint, request, jsonify
from src.services.clase_service import ClaseService
from src.api.controllers.base_controller import handle_errors
from src.core.logging_config import get_logger
from src.utils.enums import DiaSemana

logger = get_logger(__name__)

clase_bp = Blueprint('clases', __name__, url_prefix='/api/clases')
clase_service = ClaseService()


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

