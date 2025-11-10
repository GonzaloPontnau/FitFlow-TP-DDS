"""Modelo de Lista de Espera"""
from sqlalchemy import Integer, DateTime, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from src.config.database import db


class ListaEspera(db.Model):
    """
    Representa la inscripción de un socio en la lista de espera de una clase.
    
    Cuando una clase no tiene cupo disponible, los socios pueden inscribirse
    en la lista de espera para ser notificados cuando se libere un lugar.
    """
    __tablename__ = 'lista_espera'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha_inscripcion: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    posicion: Mapped[int] = mapped_column(Integer, nullable=False)
    notificado: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_notificacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    fecha_limite_confirmacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    confirmado: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    
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
        back_populates="lista_espera"
    )
    clase: Mapped["Clase"] = relationship(
        "Clase",
        back_populates="lista_espera"
    )
    
    def __init__(self, socio: "Socio", clase: "Clase", posicion: int):
        """
        Inicializa una nueva entrada en la lista de espera.
        
        Args:
            socio: Socio que se inscribe en la lista de espera
            clase: Clase para la cual se inscribe
            posicion: Posición en la lista de espera
        """
        self.socio = socio
        self.clase = clase
        self.posicion = posicion
        self.fecha_inscripcion = datetime.utcnow()
        self.notificado = False
        self.confirmado = False
        self.activo = True
    
    def notificar(self, tiempo_limite_horas: int = 24) -> None:
        """
        Marca la entrada como notificada y establece fecha límite de confirmación.
        
        Args:
            tiempo_limite_horas: Horas disponibles para confirmar (default: 24)
        """
        self.notificado = True
        self.fecha_notificacion = datetime.utcnow()
        self.fecha_limite_confirmacion = (
            datetime.utcnow() + timedelta(hours=tiempo_limite_horas)
        )
    
    def confirmar(self) -> None:
        """Marca la entrada como confirmada por el socio"""
        self.confirmado = True
        self.activo = False
    
    def desactivar(self) -> None:
        """Desactiva la entrada (socio no confirmó o ya no aplica)"""
        self.activo = False
    
    def ha_expirado(self) -> bool:
        """Verifica si ha expirado el tiempo para confirmar"""
        if not self.notificado or not self.fecha_limite_confirmacion:
            return False
        return datetime.utcnow() > self.fecha_limite_confirmacion
    
    def puede_confirmar(self) -> bool:
        """Verifica si el socio puede confirmar su lugar"""
        return (
            self.notificado and 
            not self.confirmado and 
            self.activo and 
            not self.ha_expirado()
        )
    
    def __repr__(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (f"<ListaEspera(id={self.id}, socio_id={self.socio_id}, "
                f"clase_id={self.clase_id}, posicion={self.posicion}, "
                f"estado='{estado}')>")
