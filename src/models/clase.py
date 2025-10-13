"""Modelo de Clase"""
from sqlalchemy import Integer, String, Text, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from src.config.database import db


# Tabla de asociación many-to-many entre Clase y PlanMembresia
plan_clase_association = Table(
    'plan_clase_association',
    db.Model.metadata,
    Column('plan_id', Integer, ForeignKey('planes_membresia.id'), primary_key=True),
    Column('clase_id', Integer, ForeignKey('clases.id'), primary_key=True)
)


class Clase(db.Model):
    """
    Representa una clase grupal del gimnasio.
    
    Una clase tiene un título, descripción, entrenador asignado,
    horario y un cupo máximo de participantes.
    """
    __tablename__ = 'clases'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    cupo_maximo: Mapped[int] = mapped_column(Integer, nullable=False)
    activa: Mapped[bool] = mapped_column(default=True)
    
    # Foreign Keys
    entrenador_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('entrenadores.id'),
        nullable=False
    )
    horario_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('horarios.id'),
        nullable=False
    )
    
    # Relaciones
    entrenador: Mapped["Entrenador"] = relationship(
        "Entrenador",
        back_populates="clases"
    )
    horario: Mapped["Horario"] = relationship("Horario")
    planes: Mapped[List["PlanMembresia"]] = relationship(
        "PlanMembresia",
        secondary=plan_clase_association,
        back_populates="clases"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        back_populates="clase"
    )
    
    def __init__(self, titulo: str, descripcion: str, cupo_maximo: int,
                 entrenador: "Entrenador", horario: "Horario"):
        """
        Inicializa una nueva Clase.
        
        Args:
            titulo: Nombre de la clase
            descripcion: Descripción de la actividad
            cupo_maximo: Cantidad máxima de participantes
            entrenador: Entrenador que dicta la clase
            horario: Horario en que se dicta la clase
        """
        if cupo_maximo <= 0:
            raise ValueError("El cupo máximo debe ser mayor a 0")
        
        self.titulo = titulo
        self.descripcion = descripcion
        self.cupo_maximo = cupo_maximo
        self.entrenador = entrenador
        self.horario = horario
        self.activa = True
    
    def cupos_disponibles(self) -> int:
        """Retorna la cantidad de cupos disponibles"""
        reservas_confirmadas = sum(1 for r in self.reservas if r.confirmada)
        return self.cupo_maximo - reservas_confirmadas
    
    def tiene_cupo_disponible(self) -> bool:
        """Verifica si hay cupo disponible"""
        return self.cupos_disponibles() > 0
    
    def esta_incluida_en_plan(self, plan: "PlanMembresia") -> bool:
        """Verifica si la clase está incluida en un plan específico"""
        return plan in self.planes
    
    def desactivar(self) -> None:
        """Desactiva la clase"""
        self.activa = False
    
    def __repr__(self) -> str:
        return (f"<Clase(id={self.id}, titulo='{self.titulo}', "
                f"cupo={self.cupos_disponibles()}/{self.cupo_maximo})>")
