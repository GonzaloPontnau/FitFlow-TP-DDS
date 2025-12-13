"""
Fuente Proxy para Clases Externas (Talleres Especiales).

Este módulo simula la integración con una API REST de un proveedor
externo que ofrece talleres especiales.
"""
import random
from typing import List, Dict, Optional
from datetime import datetime, time, timedelta
from src.datasources.proxy.base_proxy import BaseProxy
from src.models.clase_externa import ClaseExterna


class ClasesExternasProxy(BaseProxy):
    """
    Proxy para integración con API de clases externas.
    
    Simula la comunicación con un servicio REST externo que provee
    información sobre talleres especiales ofrecidos por terceros.
    """
    
    # Datos simulados para talleres
    TALLERES_SIMULADOS = [
        {
            'titulo': 'Yoga al Amanecer',
            'instructor': 'María García',
            'duracion': 60,
            'cupo': 15,
            'precio': 2500.0,
            'ubicacion': 'Sala Zen'
        },
        {
            'titulo': 'CrossFit Extremo',
            'instructor': 'Carlos Rodríguez',
            'duracion': 90,
            'cupo': 20,
            'precio': 3000.0,
            'ubicacion': 'Box Principal'
        },
        {
            'titulo': 'Pilates Reformer',
            'instructor': 'Laura Martínez',
            'duracion': 45,
            'cupo': 10,
            'precio': 3500.0,
            'ubicacion': 'Sala Pilates'
        },
        {
            'titulo': 'Spinning & Music',
            'instructor': 'Diego López',
            'duracion': 50,
            'cupo': 25,
            'precio': 2000.0,
            'ubicacion': 'Sala de Spinning'
        },
        {
            'titulo': 'Meditación Mindfulness',
            'instructor': 'Ana Fernández',
            'duracion': 30,
            'cupo': 20,
            'precio': 1500.0,
            'ubicacion': 'Sala de Relax'
        },
        {
            'titulo': 'Box & Cardio',
            'instructor': 'Martín Sánchez',
            'duracion': 60,
            'cupo': 18,
            'precio': 2800.0,
            'ubicacion': 'Ring de Boxeo'
        }
    ]
    
    def __init__(self, config: Dict[str, any] = None):
        """
        Inicializa el proxy de clases externas.
        
        Args:
            config: Configuración con credenciales y endpoints
                - api_key: Clave API del proveedor
                - api_url: URL base de la API
                - proveedor: Nombre del proveedor
                - timeout: Timeout para las peticiones
        """
        super().__init__(config)
        self.api_key = self.config.get('api_key', 'external_api_key')
        self.api_url = self.config.get('api_url', 'https://api.talleres-especiales.com')
        self.proveedor = self.config.get('proveedor', 'Talleres Especiales S.A.')
        self.timeout = self.config.get('timeout', 30)
        self.conectado = False
    
    def conectar(self) -> bool:
        """
        Establece conexión con la API de clases externas.
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            print(f"[ClasesExternasProxy] Conectando a {self.api_url}...")
            print(f"[ClasesExternasProxy] Proveedor: {self.proveedor}")
            
            # Simular conexión exitosa
            self.conectado = True
            print("[ClasesExternasProxy] Conexión establecida exitosamente")
            return True
            
        except Exception as e:
            print(f"[ClasesExternasProxy] Error al conectar: {str(e)}")
            self.conectado = False
            return False
    
    def verificar_disponibilidad(self) -> bool:
        """
        Verifica si la API de clases externas está disponible.
        
        Returns:
            True si el servicio está disponible
        """
        if not self.conectado:
            return False
        
        try:
            # Simular verificación (95% de disponibilidad)
            disponible = random.random() > 0.05
            
            if disponible:
                print("[ClasesExternasProxy] API disponible")
            else:
                print("[ClasesExternasProxy] API no disponible temporalmente")
            
            return disponible
            
        except Exception as e:
            print(f"[ClasesExternasProxy] Error al verificar disponibilidad: {str(e)}")
            return False
    
    # Horarios predefinidos para cada día (para datos consistentes)
    HORARIOS_POR_DIA = {
        0: [time(hour=8, minute=0), time(hour=19, minute=0)],   # Lunes
        1: [time(hour=10, minute=30), time(hour=18, minute=0)], # Martes
        2: [time(hour=9, minute=0), time(hour=20, minute=0)],   # Miércoles
        3: [time(hour=7, minute=30), time(hour=17, minute=30)], # Jueves
        4: [time(hour=16, minute=0), time(hour=19, minute=30)], # Viernes
        5: [time(hour=10, minute=0), time(hour=12, minute=0)],  # Sábado
        6: [time(hour=11, minute=0)],                            # Domingo
    }
    
    def obtener_clases_disponibles(self, fecha_desde: datetime = None, 
                                    fecha_hasta: datetime = None) -> List[ClaseExterna]:
        """
        Obtiene las clases externas disponibles en un rango de fechas.
        
        Args:
            fecha_desde: Fecha inicial (por defecto, hoy)
            fecha_hasta: Fecha final (por defecto, +7 días)
            
        Returns:
            Lista de ClaseExterna
        """
        if not self.conectado:
            print("[ClasesExternasProxy] No hay conexión establecida")
            return []
        
        try:
            # En una implementación real:
            # GET /api/v1/classes?from={fecha_desde}&to={fecha_hasta}
            
            if fecha_desde is None:
                fecha_desde = datetime.now()
            if fecha_hasta is None:
                fecha_hasta = fecha_desde + timedelta(days=7)
            
            print(f"[ClasesExternasProxy] Obteniendo clases desde {fecha_desde.date()} "
                  f"hasta {fecha_hasta.date()}...")
            
            clases = []
            # Generar talleres de forma determinística para cada día
            dias = (fecha_hasta - fecha_desde).days + 1
            
            for dia in range(dias):
                fecha = fecha_desde + timedelta(days=dia)
                dia_semana = fecha.weekday()  # 0=Lunes, 6=Domingo
                
                # Seleccionar talleres según el día de la semana (determinístico)
                indice_taller = dia_semana % len(self.TALLERES_SIMULADOS)
                taller = self.TALLERES_SIMULADOS[indice_taller]
                
                # Generar una clase por cada horario predefinido para el día
                horarios = self.HORARIOS_POR_DIA.get(dia_semana, [time(hour=10, minute=0)])
                for i, hora in enumerate(horarios):
                    # Usar diferente taller si hay más de un horario
                    taller_idx = (indice_taller + i) % len(self.TALLERES_SIMULADOS)
                    taller_actual = self.TALLERES_SIMULADOS[taller_idx]
                    clase = self._generar_clase_externa_deterministica(taller_actual, fecha, hora)
                    clases.append(clase)
            
            print(f"[ClasesExternasProxy] {len(clases)} clases obtenidas")
            return clases
            
        except Exception as e:
            print(f"[ClasesExternasProxy] Error al obtener clases: {str(e)}")
            return []
    
    def obtener_clase_por_id(self, id_externo: str) -> Optional[ClaseExterna]:
        """
        Obtiene una clase externa específica por su ID.
        
        Args:
            id_externo: ID de la clase externa
            
        Returns:
            ClaseExterna o None si no existe
        """
        if not self.conectado:
            print("[ClasesExternasProxy] No hay conexión establecida")
            return None
        
        try:
            # En una implementación real:
            # GET /api/v1/classes/{id_externo}
            
            print(f"[ClasesExternasProxy] Obteniendo clase {id_externo}...")
            
            # Simular obtención de clase
            # En un caso real, parsearíamos la respuesta JSON
            taller = random.choice(self.TALLERES_SIMULADOS)
            fecha = datetime.now() + timedelta(days=random.randint(0, 7))
            clase = self._generar_clase_externa(taller, fecha, id_externo)
            
            print(f"[ClasesExternasProxy] Clase obtenida: {clase.titulo}")
            return clase
            
        except Exception as e:
            print(f"[ClasesExternasProxy] Error al obtener clase: {str(e)}")
            return None
    
    def inscribir_socio(self, id_externo: str, socio_id: int, 
                        email: str) -> Dict[str, any]:
        """
        Inscribe a un socio en una clase externa.
        
        Args:
            id_externo: ID de la clase externa
            socio_id: ID del socio en nuestro sistema
            email: Email del socio
            
        Returns:
            Dict con el resultado de la inscripción
        """
        if not self.conectado:
            return {
                'success': False,
                'message': 'No hay conexión establecida'
            }
        
        try:
            # En una implementación real:
            # POST /api/v1/classes/{id_externo}/enrollments
            # Body: {"customer_id": socio_id, "email": email}
            
            print(f"[ClasesExternasProxy] Inscribiendo socio {socio_id} en clase {id_externo}...")
            
            # Simular inscripción (90% éxito)
            exito = random.random() > 0.1
            
            if exito:
                codigo_inscripcion = f"EXT_{id_externo}_{socio_id}_{random.randint(1000, 9999)}"
                print(f"[ClasesExternasProxy] Inscripción exitosa: {codigo_inscripcion}")
                return {
                    'success': True,
                    'message': 'Inscripción exitosa',
                    'codigo_inscripcion': codigo_inscripcion,
                    'email_confirmacion': True
                }
            else:
                print(f"[ClasesExternasProxy] Inscripción fallida: clase llena")
                return {
                    'success': False,
                    'message': 'La clase no tiene cupo disponible'
                }
            
        except Exception as e:
            print(f"[ClasesExternasProxy] Error al inscribir: {str(e)}")
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def _generar_clase_externa(self, taller: Dict, fecha: datetime, 
                               id_externo: str = None) -> ClaseExterna:
        """
        Genera un objeto ClaseExterna a partir de datos simulados.
        
        Args:
            taller: Datos del taller
            fecha: Fecha de la clase
            id_externo: ID opcional (si no se provee, se genera uno)
            
        Returns:
            ClaseExterna
        """
        if id_externo is None:
            id_externo = f"EXT_{fecha.strftime('%Y%m%d')}_{random.randint(1000, 9999)}"
        
        # Generar hora de inicio aleatoria entre 7:00 y 20:00
        hora_inicio = time(hour=random.randint(7, 20), minute=random.choice([0, 30]))
        
        # Calcular hora de fin
        duracion = taller['duracion']
        hora_fin_dt = datetime.combine(fecha, hora_inicio) + timedelta(minutes=duracion)
        hora_fin = hora_fin_dt.time()
        
        # Simular ocupación (30-90% del cupo)
        cupo_maximo = taller['cupo']
        cupos_ocupados = random.randint(int(cupo_maximo * 0.3), int(cupo_maximo * 0.9))
        
        return ClaseExterna(
            id_externo=id_externo,
            titulo=taller['titulo'],
            descripcion=f"Taller especial de {taller['titulo']} impartido por {taller['instructor']}",
            instructor=taller['instructor'],
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_minutos=duracion,
            cupo_maximo=cupo_maximo,
            cupos_ocupados=cupos_ocupados,
            precio=taller['precio'],
            ubicacion=taller['ubicacion'],
            proveedor=self.proveedor,
            url_inscripcion=f"{self.api_url}/enroll/{id_externo}"
        )
    
    def _generar_clase_externa_deterministica(self, taller: Dict, fecha: datetime, 
                                               hora_inicio: time) -> ClaseExterna:
        """
        Genera un objeto ClaseExterna con datos determinísticos para demo.
        
        Args:
            taller: Datos del taller
            fecha: Fecha de la clase
            hora_inicio: Hora de inicio predefinida
            
        Returns:
            ClaseExterna
        """
        # ID determinístico basado en fecha y título
        id_externo = f"EXT_{fecha.strftime('%Y%m%d')}_{taller['titulo'].replace(' ', '_')}"
        
        # Calcular hora de fin
        duracion = taller['duracion']
        hora_fin_dt = datetime.combine(fecha, hora_inicio) + timedelta(minutes=duracion)
        hora_fin = hora_fin_dt.time()
        
        # Ocupación determinística basada en el día de la semana (50-70%)
        cupo_maximo = taller['cupo']
        dia_semana = fecha.weekday()
        porcentaje_ocupacion = 0.5 + (dia_semana * 0.03)  # Va de 50% a 68%
        cupos_ocupados = int(cupo_maximo * porcentaje_ocupacion)
        
        return ClaseExterna(
            id_externo=id_externo,
            titulo=taller['titulo'],
            descripcion=f"Taller especial de {taller['titulo']} impartido por {taller['instructor']}",
            instructor=taller['instructor'],
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_minutos=duracion,
            cupo_maximo=cupo_maximo,
            cupos_ocupados=cupos_ocupados,
            precio=taller['precio'],
            ubicacion=taller['ubicacion'],
            proveedor=self.proveedor,
            url_inscripcion=f"{self.api_url}/enroll/{id_externo}"
        )
    
    def desconectar(self) -> None:
        """Cierra la conexión con la API."""
        if self.conectado:
            print("[ClasesExternasProxy] Cerrando conexión...")
            self.conectado = False
            print("[ClasesExternasProxy] Conexión cerrada")

