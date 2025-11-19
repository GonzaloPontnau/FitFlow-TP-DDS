from flask import Blueprint, jsonify
from src.services.estadisticas_service import EstadisticasService

estadisticas_bp = Blueprint('estadisticas', __name__, url_prefix='/api/estadisticas')
service = EstadisticasService()

@estadisticas_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    """Obtiene estadísticas generales para el dashboard"""
    stats = service.get_dashboard_stats()
    return jsonify(stats)
