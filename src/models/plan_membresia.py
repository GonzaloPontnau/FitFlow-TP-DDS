"""Modelo de Plan de Membresía"""
from sqlalchemy import Integer, String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from src.config.database import db


class PlanMembresia(db.Model):
    """
    Representa un plan de membresía del gimnasio.
    
    Un plan define el tipo de abono que un socio puede contratar,
    incluyendo qué clases puede acceder y su precio.
    """
    __tablename__ = 'planes_membresia'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    precio: Mapped[float] = mapped_column(Float, nullable=False)
    activo: Mapped[bool] = mapped_column(default=True)
    
    # Relaciones
    socios: Mapped[List["Socio"]] = relationship(
        "Socio", 
        back_populates="plan_membresia"
    )
    clases: Mapped[List["Clase"]] = relationship(
        "Clase",
        secondary="plan_clase_association",
        back_populates="planes"
    )
    
    def __init__(self, titulo: str, descripcion: str, precio: float):
        """
        Inicializa un nuevo Plan de Membresía.
        
        Args:
            titulo: Nombre del plan
            descripcion: Descripción detallada del plan
            precio: Precio mensual del plan
        """
        self.titulo = titulo
        self.descripcion = descripcion
        self.precio = precio
        self.activo = True
    
    def agregar_clase(self, clase: "Clase") -> None:
        """Agrega una clase al plan"""
        if clase not in self.clases:
            self.clases.append(clase)
    
    def quitar_clase(self, clase: "Clase") -> None:
        """Quita una clase del plan"""
        if clase in self.clases:
            self.clases.remove(clase)
    
    def desactivar(self) -> None:
        """Desactiva el plan (no se puede asignar a nuevos socios)"""
        self.activo = False
    
    def __repr__(self) -> str:
        return f"<PlanMembresia(id={self.id}, titulo='{self.titulo}', precio={self.precio})>"
