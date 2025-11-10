"""Servicio de Gestión de Listas de Espera"""
from typing import List, Optional
from datetime import datetime, timedelta
from src.models.lista_espera import ListaEspera
from src.models.clase import Clase
from src.models.socio import Socio
from src.models.reserva import Reserva
from src.repositories.base_repository import BaseRepository
from src.config.database import db
from src.core.logging_config import get_logger
from src.exceptions.base_exceptions import ValidationException, BusinessException

logger = get_logger(__name__)


class ListaEsperaRepository(BaseRepository[ListaEspera]):
    """Repositorio para operaciones de lista de espera"""
    
    def __init__(self):
        super().__init__(ListaEspera)
    
    def obtener_por_clase(self, clase_id: int, solo_activos: bool = True) -> List[ListaEspera]:
        """Obtiene todas las entradas de lista de espera de una clase"""
        query = self.model_class.query.filter_by(clase_id=clase_id)
        if solo_activos:
            query = query.filter_by(activo=True)
        return query.order_by(ListaEspera.posicion).all()
    
    def obtener_siguiente_posicion(self, clase_id: int) -> int:
        """Obtiene la siguiente posición disponible en la lista de espera"""
        ultima = (self.model_class.query
                  .filter_by(clase_id=clase_id)
                  .order_by(ListaEspera.posicion.desc())
                  .first())
        return (ultima.posicion + 1) if ultima else 1
    
    def obtener_por_socio_clase(self, socio_id: int, clase_id: int) -> Optional[ListaEspera]:
        """Obtiene la entrada de lista de espera de un socio en una clase"""
        return (self.model_class.query
                .filter_by(socio_id=socio_id, clase_id=clase_id, activo=True)
                .first())
    
    def obtener_notificados_sin_confirmar(self) -> List[ListaEspera]:
        """Obtiene entradas notificadas que aún no han sido confirmadas"""
        return (self.model_class.query
                .filter_by(notificado=True, confirmado=False, activo=True)
                .all())


class ListaEsperaService:
    """
    Servicio para gestión de listas de espera de clases.
    
    Permite a los socios inscribirse en lista de espera cuando una clase
    no tiene cupo disponible, y gestiona la asignación automática de lugares
    cuando se liberan cupos.
    """
    
    def __init__(self):
        self.lista_espera_repo = ListaEsperaRepository()
        self.tiempo_limite_confirmacion = 24  # horas
    
    def habilitar_lista_espera(self, clase: Clase) -> None:
        """
        Habilita la lista de espera para una clase.
        
        Args:
            clase: Clase a la que se le habilitará lista de espera
            
        Raises:
            BusinessException: Si la clase ya tiene lista de espera habilitada
        """
        if clase.tiene_lista_espera:
            raise BusinessException(
                f"La clase '{clase.titulo}' ya tiene lista de espera habilitada"
            )
        
        clase.tiene_lista_espera = True
        db.session.commit()
        logger.info(f"Lista de espera habilitada para clase {clase.id}")
    
    def deshabilitar_lista_espera(self, clase: Clase) -> None:
        """
        Deshabilita la lista de espera para una clase.
        
        Args:
            clase: Clase a la que se le deshabilitará lista de espera
        """
        if not clase.tiene_lista_espera:
            return
        
        # Desactivar todas las entradas de lista de espera
        entradas = self.lista_espera_repo.obtener_por_clase(clase.id)
        for entrada in entradas:
            entrada.desactivar()
        
        clase.tiene_lista_espera = False
        db.session.commit()
        logger.info(f"Lista de espera deshabilitada para clase {clase.id}")
    
    def inscribir_en_lista_espera(self, socio: Socio, clase: Clase) -> ListaEspera:
        """
        Inscribe a un socio en la lista de espera de una clase.
        
        Args:
            socio: Socio que se inscribe
            clase: Clase a la que se inscribe
            
        Returns:
            Entrada de lista de espera creada
            
        Raises:
            BusinessException: Si la clase no tiene lista de espera habilitada
            ValidationException: Si el socio ya está en la lista de espera
        """
        if not clase.tiene_lista_espera:
            raise BusinessException(
                f"La clase '{clase.titulo}' no tiene lista de espera habilitada"
            )
        
        # Verificar que el socio no esté ya en la lista de espera
        entrada_existente = self.lista_espera_repo.obtener_por_socio_clase(
            socio.id, clase.id
        )
        if entrada_existente:
            raise ValidationException(
                f"El socio ya está inscrito en la lista de espera de esta clase",
                field="socio_id"
            )
        
        # Obtener siguiente posición
        posicion = self.lista_espera_repo.obtener_siguiente_posicion(clase.id)
        
        # Crear entrada en lista de espera
        entrada = ListaEspera(socio=socio, clase=clase, posicion=posicion)
        entrada = self.lista_espera_repo.create(entrada)
        
        logger.info(
            f"Socio {socio.id} inscrito en lista de espera de clase {clase.id} "
            f"(posición {posicion})"
        )
        
        return entrada
    
    def cancelar_inscripcion_lista_espera(
        self, socio: Socio, clase: Clase
    ) -> None:
        """
        Cancela la inscripción de un socio en la lista de espera.
        
        Args:
            socio: Socio que cancela
            clase: Clase de la que se cancela
            
        Raises:
            BusinessException: Si el socio no está en la lista de espera
        """
        entrada = self.lista_espera_repo.obtener_por_socio_clase(
            socio.id, clase.id
        )
        
        if not entrada:
            raise BusinessException(
                "El socio no está en la lista de espera de esta clase"
            )
        
        entrada.desactivar()
        db.session.commit()
        
        logger.info(
            f"Socio {socio.id} canceló inscripción en lista de espera "
            f"de clase {clase.id}"
        )
    
    def obtener_lista_espera_clase(self, clase_id: int) -> List[ListaEspera]:
        """
        Obtiene la lista de espera completa de una clase.
        
        Args:
            clase_id: ID de la clase
            
        Returns:
            Lista de entradas ordenadas por posición
        """
        return self.lista_espera_repo.obtener_por_clase(clase_id)
    
    def notificar_siguiente_en_lista(
        self, clase: Clase, tiempo_limite_horas: int = None
    ) -> Optional[ListaEspera]:
        """
        Notifica al siguiente socio en la lista de espera que hay un lugar disponible.
        
        Args:
            clase: Clase con lugar disponible
            tiempo_limite_horas: Horas para confirmar (default: 24)
            
        Returns:
            Entrada notificada o None si no hay nadie en la lista
        """
        if tiempo_limite_horas is None:
            tiempo_limite_horas = self.tiempo_limite_confirmacion
        
        # Obtener primera entrada activa de la lista
        entradas = self.lista_espera_repo.obtener_por_clase(clase.id, solo_activos=True)
        
        if not entradas:
            logger.info(f"No hay personas en lista de espera para clase {clase.id}")
            return None
        
        primera_entrada = entradas[0]
        primera_entrada.notificar(tiempo_limite_horas)
        db.session.commit()
        
        logger.info(
            f"Notificado socio {primera_entrada.socio.id} de lista de espera "
            f"para clase {clase.id}"
        )
        
        # En un sistema real, aquí se enviaría un email o notificación push
        self._enviar_notificacion(primera_entrada)
        
        return primera_entrada
    
    def _enviar_notificacion(self, entrada: ListaEspera) -> None:
        """
        Envía notificación al socio (simulado).
        
        En producción, esto enviaría un email o notificación push.
        """
        logger.info(
            f"[NOTIFICACIÓN] Enviando email a {entrada.socio.email}: "
            f"Hay un lugar disponible en '{entrada.clase.titulo}'. "
            f"Tienes hasta {entrada.fecha_limite_confirmacion.strftime('%Y-%m-%d %H:%M')} "
            f"para confirmar."
        )
    
    def confirmar_lugar(self, socio: Socio, clase: Clase) -> Reserva:
        """
        Confirma el lugar del socio que fue notificado de la lista de espera.
        
        Args:
            socio: Socio que confirma
            clase: Clase a la que accede
            
        Returns:
            Reserva creada
            
        Raises:
            BusinessException: Si no puede confirmar (no notificado, expirado, etc.)
        """
        entrada = self.lista_espera_repo.obtener_por_socio_clase(
            socio.id, clase.id
        )
        
        if not entrada:
            raise BusinessException(
                "El socio no está en la lista de espera de esta clase"
            )
        
        if not entrada.puede_confirmar():
            if entrada.ha_expirado():
                raise BusinessException(
                    "El tiempo para confirmar ha expirado"
                )
            elif not entrada.notificado:
                raise BusinessException(
                    "Aún no has sido notificado de un lugar disponible"
                )
            else:
                raise BusinessException(
                    "No puedes confirmar en este momento"
                )
        
        # Verificar que aún hay cupo (por si acaso)
        if not clase.tiene_cupo_disponible():
            raise BusinessException(
                "Ya no hay cupo disponible en esta clase"
            )
        
        # Crear reserva
        from src.repositories.base_repository import BaseRepository
        reserva = Reserva(socio=socio, clase=clase)
        reserva_repo = BaseRepository(Reserva)
        reserva = reserva_repo.create(reserva)
        
        # Confirmar y desactivar entrada de lista de espera
        entrada.confirmar()
        db.session.commit()
        
        logger.info(
            f"Socio {socio.id} confirmó lugar desde lista de espera "
            f"para clase {clase.id}"
        )
        
        return reserva
    
    def procesar_expirados(self) -> int:
        """
        Procesa las entradas de lista de espera que expiraron sin confirmar.
        
        Returns:
            Cantidad de entradas procesadas
        """
        entradas_notificadas = self.lista_espera_repo.obtener_notificados_sin_confirmar()
        procesadas = 0
        
        for entrada in entradas_notificadas:
            if entrada.ha_expirado():
                entrada.desactivar()
                procesadas += 1
                logger.info(
                    f"Entrada de lista de espera {entrada.id} expirada "
                    f"(socio {entrada.socio.id}, clase {entrada.clase.id})"
                )
                
                # Notificar al siguiente si hay cupo disponible
                if entrada.clase.tiene_cupo_disponible():
                    self.notificar_siguiente_en_lista(entrada.clase)
        
        if procesadas > 0:
            db.session.commit()
        
        logger.info(f"Procesadas {procesadas} entradas expiradas de lista de espera")
        return procesadas
    
    def procesar_liberaciones_cupos(self) -> int:
        """
        Procesa las clases que tienen cupo disponible y lista de espera pendiente.
        
        Debe ejecutarse periódicamente (ej. cada noche) para notificar
        a las personas en lista de espera.
        
        Returns:
            Cantidad de notificaciones enviadas
        """
        # Primero procesar expirados
        self.procesar_expirados()
        
        notificaciones = 0
        
        # Obtener todas las clases con lista de espera habilitada
        from src.repositories.clase_repository import ClaseRepository
        clase_repo = ClaseRepository()
        clases_con_lista = clase_repo.find_by_field('tiene_lista_espera', True)
        
        for clase in clases_con_lista:
            # Si la clase tiene cupo disponible y hay personas en lista de espera
            if clase.tiene_cupo_disponible():
                entradas_activas = self.lista_espera_repo.obtener_por_clase(
                    clase.id, solo_activos=True
                )
                
                # Filtrar las que no han sido notificadas
                entradas_sin_notificar = [
                    e for e in entradas_activas if not e.notificado
                ]
                
                # Notificar hasta llenar el cupo disponible
                cupos_disponibles = clase.cupos_disponibles()
                for entrada in entradas_sin_notificar[:cupos_disponibles]:
                    self.notificar_siguiente_en_lista(clase)
                    notificaciones += 1
        
        logger.info(
            f"Procesamiento de liberación de cupos completado: "
            f"{notificaciones} notificaciones enviadas"
        )
        
        return notificaciones
