"""Controlador REST para Pagos"""
from flask import Blueprint, request, jsonify
from src.services.pago_service import PagoService
from src.api.controllers.base_controller import handle_errors, validate_json
from src.core.logging_config import get_logger

logger = get_logger(__name__)

pago_bp = Blueprint('pagos', __name__, url_prefix='/api/pagos')
pago_service = PagoService()


@pago_bp.route('', methods=['POST'])
@handle_errors
@validate_json('socio_id', 'mes_periodo', 'anio_periodo')
def registrar_pago():
    """
    Registra un nuevo pago.
    
    Body JSON:
        {
            "socio_id": 1,
            "mes_periodo": 2,
            "anio_periodo": 2025
        }
    
    Returns:
        201: Pago registrado
        400: Error de validación
    """
    data = request.get_json()
    
    resultado = pago_service.registrar_pago(
        socio_id=data['socio_id'],
        mes_periodo=data['mes_periodo'],
        anio_periodo=data['anio_periodo']
    )
    
    if resultado['success']:
        pago = resultado['pago']
        return jsonify({
            'success': True,
            'message': resultado['message'],
            'data': {
                'pago_id': pago.id,
                'referencia': pago.referencia_externa,
                'monto': pago.monto,
                'estado': pago.estado.value
            }
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': resultado['message']
        }), 400


@pago_bp.route('/verificar-pendientes', methods=['POST'])
@handle_errors
def verificar_pagos_pendientes():
    """
    Verifica el estado de todos los pagos pendientes con la pasarela.
    
    Endpoint administrativo para ejecutar la verificación diaria.
    
    Returns:
        200: Resultado de la verificación
    """
    resultado = pago_service.verificar_pagos_pendientes()
    
    status_code = 200 if resultado['success'] else 500
    
    return jsonify({
        'success': resultado['success'],
        'message': resultado['message'],
        'data': {
            'verificados': resultado['verificados'],
            'aprobados': resultado['aprobados'],
            'rechazados': resultado['rechazados']
        }
    }), status_code


@pago_bp.route('/socio/<int:socio_id>', methods=['GET'])
@handle_errors
def listar_pagos_socio(socio_id: int):
    """
    Lista los pagos de un socio.
    
    Args:
        socio_id: ID del socio
    
    Returns:
        200: Lista de pagos
    """
    pagos = pago_service.listar_pagos_socio(socio_id)
    
    return jsonify({
        'success': True,
        'count': len(pagos),
        'data': [
            {
                'id': p.id,
                'monto': p.monto,
                'estado': p.estado.value,
                'fecha_pago': p.fecha_pago.isoformat(),
                'periodo': f"{p.mes_periodo:02d}/{p.anio_periodo}",
                'referencia': p.referencia_externa
            }
            for p in pagos
        ]
    }), 200

