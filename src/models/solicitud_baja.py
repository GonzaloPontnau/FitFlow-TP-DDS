"""Modelo de Solicitud de Baja"""
from sqlalchemy import Integer, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.config.database import db
from src.utils.enums import EstadoSolicitudBaja, LONGITUD_MINIMA_SOLICITUD_BAJA


class SolicitudBaja(db.Model):
    """
    Representa una solicitud de baja de membresía.
    
    Un socio puede solicitar la baja de su membresía proporcionando
    una justificación. La solicitud debe ser aprobada o rechazada
    por un administrador.
    """
    __tablename__ = 'solicitudes_baja'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    justificacion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    estado: Mapped[EstadoSolicitudBaja] = mapped_column(
        Enum(EstadoSolicitudBaja),
        default=EstadoSolicitudBaja.PENDIENTE
    )
    fecha_resolucion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    comentario_admin: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Foreign Key
    socio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('socios.id'),
        nullable=False
    )
    
    # Relaciones
    socio: Mapped["Socio"] = relationship(
        "Socio",
        back_populates="solicitudes_baja"
    )
    
    def __init__(self, socio: "Socio", justificacion: str):
        """
        Inicializa una nueva Solicitud de Baja.
        
        Args:
            socio: Socio que solicita la baja
            justificacion: Texto justificando la solicitud
            
        Raises:
            ValueError: Si la justificación no cumple con la longitud mínima
        """
        if len(justificacion) < LONGITUD_MINIMA_SOLICITUD_BAJA:
            raise ValueError(
                f"La justificación debe tener al menos "
                f"{LONGITUD_MINIMA_SOLICITUD_BAJA} caracteres"
            )
        
        self.socio = socio
        self.justificacion = justificacion
        self.fecha_solicitud = datetime.utcnow()
        self.estado = EstadoSolicitudBaja.PENDIENTE
    
    def aprobar(self, comentario_admin: str = None) -> None:
        """
        Aprueba la solicitud de baja.
        
        Args:
            comentario_admin: Comentario opcional del administrador
        """
        if self.estado != EstadoSolicitudBaja.PENDIENTE:
            raise ValueError("Solo se pueden aprobar solicitudes pendientes")
        
        self.estado = EstadoSolicitudBaja.APROBADA
        self.fecha_resolucion = datetime.utcnow()
        self.comentario_admin = comentario_admin
        self.socio.dar_de_baja()
    
    def rechazar(self, comentario_admin: str) -> None:
        """
        Rechaza la solicitud de baja.
        
        Args:
            comentario_admin: Motivo del rechazo
        """
        if self.estado != EstadoSolicitudBaja.PENDIENTE:
            raise ValueError("Solo se pueden rechazar solicitudes pendientes")
        
        self.estado = EstadoSolicitudBaja.RECHAZADA
        self.fecha_resolucion = datetime.utcnow()
        self.comentario_admin = comentario_admin
    
    def esta_pendiente(self) -> bool:
        """Verifica si la solicitud está pendiente"""
        return self.estado == EstadoSolicitudBaja.PENDIENTE
    
    def __repr__(self) -> str:
        return (f"<SolicitudBaja(id={self.id}, socio_id={self.socio_id}, "
                f"estado='{self.estado.value}', fecha={self.fecha_solicitud})>")
