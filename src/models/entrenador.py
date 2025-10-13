"""Modelo de Entrenador"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from src.config.database import db


class Entrenador(db.Model):
    """
    Representa un entrenador del gimnasio.
    
    Un entrenador puede dictar múltiples clases.
    """
    __tablename__ = 'entrenadores'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    especialidad: Mapped[str] = mapped_column(String(200), nullable=True)
    activo: Mapped[bool] = mapped_column(default=True)
    
    # Relaciones
    clases: Mapped[List["Clase"]] = relationship(
        "Clase",
        back_populates="entrenador"
    )
    
    def __init__(self, nombre: str, apellido: str, email: str, 
                 especialidad: str = None):
        """
        Inicializa un nuevo Entrenador.
        
        Args:
            nombre: Nombre del entrenador
            apellido: Apellido del entrenador
            email: Email de contacto
            especialidad: Especialidad o certificaciones del entrenador
        """
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.especialidad = especialidad
        self.activo = True
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del entrenador"""
        return f"{self.nombre} {self.apellido}"
    
    def desactivar(self) -> None:
        """Desactiva al entrenador"""
        self.activo = False
    
    def __repr__(self) -> str:
        return f"<Entrenador(id={self.id}, nombre='{self.nombre_completo}')>"
