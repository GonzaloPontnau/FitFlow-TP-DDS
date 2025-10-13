"""Modelo de Horario"""
from sqlalchemy import Integer, String, Time, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import time
from src.config.database import db
from src.utils.enums import DiaSemana


class Horario(db.Model):
    """
    Representa un horario específico para una clase.
    
    Define el día de la semana, hora de inicio y duración de una clase.
    """
    __tablename__ = 'horarios'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dia_semana: Mapped[DiaSemana] = mapped_column(
        Enum(DiaSemana),
        nullable=False
    )
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fin: Mapped[time] = mapped_column(Time, nullable=False)
    
    def __init__(self, dia_semana: DiaSemana, hora_inicio: time, hora_fin: time):
        """
        Inicializa un nuevo Horario.
        
        Args:
            dia_semana: Día de la semana
            hora_inicio: Hora de inicio de la clase
            hora_fin: Hora de finalización de la clase
        """
        if hora_fin <= hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        
        self.dia_semana = dia_semana
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
    
    def duracion_minutos(self) -> int:
        """Calcula la duración de la clase en minutos"""
        delta = (
            self.hora_fin.hour * 60 + self.hora_fin.minute -
            self.hora_inicio.hour * 60 - self.hora_inicio.minute
        )
        return delta
    
    def __repr__(self) -> str:
        return (f"<Horario(dia={self.dia_semana.value}, "
                f"inicio={self.hora_inicio}, fin={self.hora_fin})>")
