"""Modelo de Reserva"""
from sqlalchemy import Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.config.database import db


class Reserva(db.Model):
    """
    Representa la reserva de un socio a una clase.
    
    Una reserva vincula a un socio con una clase específica
    en una fecha determinada.
    """
    __tablename__ = 'reservas'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_reserva: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    confirmada: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_cancelacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    
    # Foreign Keys
    socio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('socios.id'),
        nullable=False
    )
    clase_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('clases.id'),
        nullable=False
    )
    
    # Relaciones
    socio: Mapped["Socio"] = relationship(
        "Socio",
        back_populates="reservas"
    )
    clase: Mapped["Clase"] = relationship(
        "Clase",
        back_populates="reservas"
    )
    
    def __init__(self, socio: "Socio", clase: "Clase"):
        """
        Inicializa una nueva Reserva.
        
        Args:
            socio: Socio que realiza la reserva
            clase: Clase a la que se reserva
        """
        self.socio = socio
        self.clase = clase
        self.fecha_reserva = datetime.utcnow()
        self.confirmada = True
    
    def cancelar(self) -> None:
        """Cancela la reserva"""
        self.confirmada = False
        self.fecha_cancelacion = datetime.utcnow()
    
    def esta_activa(self) -> bool:
        """Verifica si la reserva está activa"""
        return self.confirmada and self.fecha_cancelacion is None
    
    def __repr__(self) -> str:
        estado = "Confirmada" if self.confirmada else "Cancelada"
        return (f"<Reserva(id={self.id}, socio_id={self.socio_id}, "
                f"clase_id={self.clase_id}, estado='{estado}')>")
