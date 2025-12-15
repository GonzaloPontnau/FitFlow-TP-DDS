"""Controlador REST para Planes de Membresía"""
from flask import Blueprint, request, jsonify
from src.services.plan_service import PlanService
from src.services.clase_service import ClaseService
from src.api.controllers.base_controller import handle_errors, validate_json
from src.core.logging_config import get_logger
from src.config.database import db

logger = get_logger(__name__)

plan_bp = Blueprint('planes', __name__, url_prefix='/api/planes')
plan_service = PlanService()
clase_service = ClaseService()


@plan_bp.route('', methods=['GET'])
@handle_errors
def listar_planes():
    """
    Lista todos los planes de membresía activos.
    
    Returns:
        200: Lista de planes
    """
    # Forzar que SQLAlchemy lea datos frescos de la BD
    db.session.expire_all()
    planes = plan_service.listar_planes_activos()
    
    return jsonify({
        'success': True,
        'count': len(planes),
        'data': [
            {
                'id': plan.id,
                'titulo': plan.titulo,
                'descripcion': plan.descripcion,
                'precio': plan.precio,
                'nivel': plan.nivel,
                'cantidad_clases': len(plan.clases),
                'activo': plan.activo
            }
            for plan in planes
        ]
    }), 200


@plan_bp.route('/<int:plan_id>', methods=['GET'])
@handle_errors
def obtener_plan(plan_id: int):
    """
    Obtiene información detallada de un plan de membresía.
    
    Args:
        plan_id: ID del plan
    
    Returns:
        200: Información del plan
        404: Plan no encontrado
    """
    plan = plan_service.obtener_plan(plan_id)
    
    if not plan:
        return jsonify({
            'success': False,
            'message': f'Plan con ID {plan_id} no encontrado'
        }), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': plan.id,
            'titulo': plan.titulo,
            'descripcion': plan.descripcion,
            'precio': plan.precio,
            'nivel': plan.nivel,
            'activo': plan.activo,
            'clases': [
                {
                    'id': clase.id,
                    'titulo': clase.titulo,
                    'entrenador': clase.entrenador.nombre_completo,
                    'dia': clase.horario.dia_semana.value,
                    'hora_inicio': clase.horario.hora_inicio.strftime('%H:%M') if clase.horario.hora_inicio else None
                }
                for clase in plan.clases
            ]
        }
    }), 200


@plan_bp.route('', methods=['POST'])
@handle_errors
@validate_json('titulo', 'descripcion', 'precio')
def crear_plan():
    """
    Crea un nuevo plan de membresía.
    
    Body JSON:
        titulo: Nombre del plan
        descripcion: Descripción del plan
        precio: Precio mensual
        nivel: Nivel del plan (1, 2 o 3) - opcional, default 1
    
    Returns:
        201: Plan creado
        400: Datos inválidos
    """
    data = request.get_json()
    
    nivel = data.get('nivel', 1)
    
    plan = plan_service.crear_plan(
        titulo=data['titulo'],
        descripcion=data['descripcion'],
        precio=data['precio'],
        nivel=nivel
    )
    
    logger.info(f"Plan creado: {plan.id} - {plan.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Plan creado exitosamente',
        'data': {
            'id': plan.id,
            'titulo': plan.titulo,
            'descripcion': plan.descripcion,
            'precio': plan.precio,
            'nivel': plan.nivel
        }
    }), 201


@plan_bp.route('/<int:plan_id>', methods=['PUT'])
@handle_errors
def actualizar_plan(plan_id: int):
    """
    Actualiza un plan de membresía existente.
    
    Args:
        plan_id: ID del plan
    
    Body JSON (todos opcionales):
        titulo: Nuevo nombre
        descripcion: Nueva descripción
        precio: Nuevo precio
        nivel: Nuevo nivel (1, 2 o 3)
        activo: Estado del plan
    
    Returns:
        200: Plan actualizado
        404: Plan no encontrado
    """
    plan = plan_service.obtener_plan(plan_id)
    if not plan:
        return jsonify({
            'success': False,
            'message': f'Plan con ID {plan_id} no encontrado'
        }), 404
    
    data = request.get_json()
    
    # Actualizar campos si están presentes
    if 'titulo' in data:
        plan.titulo = data['titulo']
    if 'descripcion' in data:
        plan.descripcion = data['descripcion']
    if 'precio' in data:
        if data['precio'] <= 0:
            return jsonify({
                'success': False,
                'message': 'El precio debe ser mayor a 0'
            }), 400
        plan.precio = data['precio']
    if 'nivel' in data:
        if data['nivel'] not in [1, 2, 3]:
            return jsonify({
                'success': False,
                'message': 'El nivel debe ser 1, 2 o 3'
            }), 400
        plan.nivel = data['nivel']
    if 'activo' in data:
        plan.activo = bool(data['activo'])
    
    db.session.commit()
    
    logger.info(f"Plan actualizado: {plan.id} - {plan.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Plan actualizado exitosamente',
        'data': {
            'id': plan.id,
            'titulo': plan.titulo,
            'descripcion': plan.descripcion,
            'precio': plan.precio,
            'nivel': plan.nivel,
            'activo': plan.activo
        }
    }), 200


@plan_bp.route('/<int:plan_id>', methods=['DELETE'])
@handle_errors
def eliminar_plan(plan_id: int):
    """
    Elimina (desactiva) un plan de membresía.
    
    Args:
        plan_id: ID del plan
    
    Returns:
        200: Plan eliminado
        404: Plan no encontrado
    """
    plan = plan_service.obtener_plan(plan_id)
    if not plan:
        return jsonify({
            'success': False,
            'message': f'Plan con ID {plan_id} no encontrado'
        }), 404
    
    plan.activo = False
    db.session.commit()
    
    logger.info(f"Plan desactivado: {plan.id} - {plan.titulo}")
    
    return jsonify({
        'success': True,
        'message': 'Plan eliminado exitosamente'
    }), 200


@plan_bp.route('/<int:plan_id>/clases/<int:clase_id>', methods=['POST'])
@handle_errors
def agregar_clase_a_plan(plan_id: int, clase_id: int):
    """
    Agrega una clase a un plan de membresía.
    
    Args:
        plan_id: ID del plan
        clase_id: ID de la clase
    
    Returns:
        200: Clase agregada
        404: Plan o clase no encontrados
        400: La clase ya está en el plan
    """
    plan = plan_service.obtener_plan(plan_id)
    if not plan:
        return jsonify({
            'success': False,
            'message': f'Plan con ID {plan_id} no encontrado'
        }), 404
    
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    if clase in plan.clases:
        return jsonify({
            'success': False,
            'message': 'La clase ya está incluida en el plan'
        }), 400
    
    plan.agregar_clase(clase)
    db.session.commit()
    
    logger.info(f"Clase {clase_id} agregada a plan {plan_id}")
    
    return jsonify({
        'success': True,
        'message': f'Clase "{clase.titulo}" agregada al plan "{plan.titulo}"'
    }), 200


@plan_bp.route('/<int:plan_id>/clases/<int:clase_id>', methods=['DELETE'])
@handle_errors
def quitar_clase_de_plan(plan_id: int, clase_id: int):
    """
    Quita una clase de un plan de membresía.
    
    Args:
        plan_id: ID del plan
        clase_id: ID de la clase
    
    Returns:
        200: Clase quitada
        404: Plan o clase no encontrados
        400: La clase no está en el plan
    """
    plan = plan_service.obtener_plan(plan_id)
    if not plan:
        return jsonify({
            'success': False,
            'message': f'Plan con ID {plan_id} no encontrado'
        }), 404
    
    clase = clase_service.obtener_clase(clase_id)
    if not clase:
        return jsonify({
            'success': False,
            'message': f'Clase con ID {clase_id} no encontrada'
        }), 404
    
    if clase not in plan.clases:
        return jsonify({
            'success': False,
            'message': 'La clase no está incluida en el plan'
        }), 400
    
    plan.quitar_clase(clase)
    db.session.commit()
    
    logger.info(f"Clase {clase_id} quitada de plan {plan_id}")
    
    return jsonify({
        'success': True,
        'message': f'Clase "{clase.titulo}" quitada del plan "{plan.titulo}"'
    }), 200
