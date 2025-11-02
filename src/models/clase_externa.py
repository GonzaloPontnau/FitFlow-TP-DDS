"""Modelo de Clase Externa (Taller Especial)"""
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class ClaseExterna:
    """
    Representa una clase o taller externo ofrecido por un proveedor externo.
    
    No se persiste en la base de datos, se obtiene en tiempo real
    desde la API del proveedor externo.
    """
    id_externo: str
    titulo: str
    descripcion: str
    instructor: str
    fecha: datetime
    hora_inicio: time
    hora_fin: time
    duracion_minutos: int
    cupo_maximo: int
    cupos_ocupados: int
    precio: float
    ubicacion: str
    proveedor: str
    url_inscripcion: Optional[str] = None
    
    @property
    def cupos_disponibles(self) -> int:
        """Retorna la cantidad de cupos disponibles"""
        return max(0, self.cupo_maximo - self.cupos_ocupados)
    
    @property
    def tiene_cupo(self) -> bool:
        """Verifica si hay cupo disponible"""
        return self.cupos_disponibles > 0
    
    @property
    def porcentaje_ocupacion(self) -> float:
        """Retorna el porcentaje de ocupación"""
        if self.cupo_maximo == 0:
            return 0.0
        return (self.cupos_ocupados / self.cupo_maximo) * 100
    
    def __str__(self) -> str:
        return (f"{self.titulo} - {self.instructor} "
                f"({self.cupos_disponibles}/{self.cupo_maximo} cupos)")
    
    def __repr__(self) -> str:
        return (f"<ClaseExterna(id='{self.id_externo}', titulo='{self.titulo}', "
                f"fecha={self.fecha.strftime('%Y-%m-%d')}, "
                f"cupos={self.cupos_disponibles}/{self.cupo_maximo})>")

