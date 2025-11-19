from sqlalchemy import func, desc
from src.config.database import db
from src.models.clase import Clase
from src.models.reserva import Reserva
from src.models.plan_membresia import PlanMembresia
from src.models.socio import Socio
from src.models.horario import Horario

class EstadisticasService:
    def get_clase_mas_popular(self):
        """Obtiene la clase con mayor cantidad de reservas históricas"""
        result = db.session.query(
            Clase.titulo, func.count(Reserva.id).label('total')
        ).join(Reserva).filter(Reserva.confirmada == True).group_by(Clase.id, Clase.titulo).order_by(desc('total')).first()
        
        return {"clase": result[0], "reservas": result[1]} if result else None

    def get_horario_mas_concurrido(self):
        """Obtiene el horario con mayor cantidad de reservas"""
        result = db.session.query(
            Horario.dia_semana, Horario.hora_inicio, func.count(Reserva.id).label('total')
        ).join(Clase, Horario.id == Clase.horario_id).join(Reserva, Clase.id == Reserva.clase_id).filter(Reserva.confirmada == True).group_by(Horario.id, Horario.dia_semana, Horario.hora_inicio).order_by(desc('total')).first()
        
        if result:
            return {
                "dia": result[0].value,
                "hora": result[1].strftime("%H:%M"),
                "reservas": result[2]
            }
        return None

    def get_plan_mayor_ingresos(self):
        """Obtiene el plan que genera más ingresos (socios * precio)"""
        result = db.session.query(
            PlanMembresia.titulo, 
            (func.count(Socio.id) * PlanMembresia.precio).label('ingresos')
        ).join(Socio).group_by(PlanMembresia.id, PlanMembresia.titulo, PlanMembresia.precio).order_by(desc('ingresos')).first()
        
        return {"plan": result[0], "ingresos": float(result[1])} if result else None

    def get_tasa_asistencia(self):
        """Calcula el porcentaje de reservas confirmadas sobre el total"""
        total = db.session.query(func.count(Reserva.id)).scalar()
        confirmadas = db.session.query(func.count(Reserva.id)).filter(Reserva.confirmada == True).scalar()
        
        if total == 0:
            return 0.0
        return round((confirmadas / total) * 100, 2)

    def get_dashboard_stats(self):
        """Obtiene todas las estadísticas para el dashboard"""
        return {
            "clase_popular": self.get_clase_mas_popular(),
            "horario_concurrido": self.get_horario_mas_concurrido(),
            "plan_ingresos": self.get_plan_mayor_ingresos(),
            "tasa_asistencia": self.get_tasa_asistencia()
        }
