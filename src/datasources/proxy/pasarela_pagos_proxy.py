"""
Fuente Proxy para Pasarela de Pagos.

Este módulo simula la integración con una pasarela de pagos externa.
En un entorno real, se conectaría a una API de pago como Stripe, MercadoPago, etc.
"""
import random
from typing import List, Dict, Optional
from datetime import datetime, UTC
from src.datasources.proxy.base_proxy import BaseProxy
from src.models.pago import EstadoPago


class PasarelaPagosProxy(BaseProxy):
    """
    Proxy para integración con pasarela de pagos externa.
    
    Simula la comunicación con un servicio externo de procesamiento
    de pagos, verificando el estado de las transacciones.
    """
    
    def __init__(self, config: Dict[str, any] = None):
        """
        Inicializa el proxy de la pasarela de pagos.
        
        Args:
            config: Configuración con credenciales y endpoints
                - api_key: Clave API de la pasarela
                - api_url: URL base de la API
                - timeout: Timeout para las peticiones
        """
        super().__init__(config)
        self.api_key = self.config.get('api_key', 'test_api_key')
        self.api_url = self.config.get('api_url', 'https://api.pasarela-ficcticia.com')
        self.timeout = self.config.get('timeout', 30)
        self.conectado = False
    
    def conectar(self) -> bool:
        """
        Establece conexión con la pasarela de pagos.
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            # En una implementación real, aquí se haría:
            # - Validación de credenciales
            # - Handshake con la API
            # - Verificación de conectividad
            
            print(f"[PasarelaPagosProxy] Conectando a {self.api_url}...")
            print(f"[PasarelaPagosProxy] Usando API Key: {self.api_key[:10]}...")
            
            # Simular conexión exitosa
            self.conectado = True
            print("[PasarelaPagosProxy] Conexión establecida exitosamente")
            return True
            
        except Exception as e:
            print(f"[PasarelaPagosProxy] Error al conectar: {str(e)}")
            self.conectado = False
            return False
    
    def verificar_disponibilidad(self) -> bool:
        """
        Verifica si la pasarela de pagos está disponible.
        
        Returns:
            True si el servicio está disponible
        """
        if not self.conectado:
            return False
        
        try:
            # En una implementación real, haría un health check
            # GET /health o /status
            
            # Simular verificación (90% de disponibilidad)
            disponible = random.random() > 0.1
            
            if disponible:
                print("[PasarelaPagosProxy] Servicio disponible")
            else:
                print("[PasarelaPagosProxy] Servicio no disponible temporalmente")
            
            return disponible
            
        except Exception as e:
            print(f"[PasarelaPagosProxy] Error al verificar disponibilidad: {str(e)}")
            return False
    
    def verificar_estado_pago(self, referencia_externa: str) -> Optional[EstadoPago]:
        """
        Verifica el estado de un pago en la pasarela externa.
        
        Args:
            referencia_externa: ID de transacción en la pasarela
            
        Returns:
            EstadoPago con el estado actual, o None si hay error
        """
        if not self.conectado:
            print("[PasarelaPagosProxy] No hay conexión establecida")
            return None
        
        try:
            # En una implementación real:
            # GET /api/v1/payments/{referencia_externa}
            # Y parsear la respuesta
            
            print(f"[PasarelaPagosProxy] Verificando pago {referencia_externa}...")
            
            # Simular respuesta de la API (80% aprobados, 10% rechazados, 10% procesando)
            rand = random.random()
            if rand < 0.80:
                estado = EstadoPago.APROBADO
            elif rand < 0.90:
                estado = EstadoPago.RECHAZADO
            else:
                estado = EstadoPago.PROCESANDO
            
            print(f"[PasarelaPagosProxy] Estado del pago: {estado.value}")
            return estado
            
        except Exception as e:
            print(f"[PasarelaPagosProxy] Error al verificar estado: {str(e)}")
            return None
    
    def verificar_estados_lote(self, referencias: List[str]) -> Dict[str, EstadoPago]:
        """
        Verifica el estado de múltiples pagos en lote.
        
        Args:
            referencias: Lista de IDs de transacciones
            
        Returns:
            Dict con referencia -> estado
        """
        if not self.conectado:
            print("[PasarelaPagosProxy] No hay conexión establecida")
            return {}
        
        try:
            # En una implementación real:
            # POST /api/v1/payments/batch-status
            # Body: {"payment_ids": referencias}
            
            print(f"[PasarelaPagosProxy] Verificando {len(referencias)} pagos en lote...")
            
            resultados = {}
            for ref in referencias:
                estado = self.verificar_estado_pago(ref)
                if estado:
                    resultados[ref] = estado
            
            print(f"[PasarelaPagosProxy] Verificados {len(resultados)} de {len(referencias)} pagos")
            return resultados
            
        except Exception as e:
            print(f"[PasarelaPagosProxy] Error en verificación de lote: {str(e)}")
            return {}
    
    def procesar_pago(self, socio_id: int, monto: float, 
                      metodo_pago: str = "tarjeta") -> Optional[str]:
        """
        Procesa un nuevo pago en la pasarela.
        
        Args:
            socio_id: ID del socio que realiza el pago
            monto: Monto a cobrar
            metodo_pago: Método de pago (tarjeta, transferencia, etc.)
            
        Returns:
            Referencia externa del pago, o None si falla
        """
        if not self.conectado:
            print("[PasarelaPagosProxy] No hay conexión establecida")
            return None
        
        try:
            # En una implementación real:
            # POST /api/v1/payments
            # Body: {
            #   "customer_id": socio_id,
            #   "amount": monto,
            #   "payment_method": metodo_pago,
            #   "currency": "ARS"
            # }
            
            print(f"[PasarelaPagosProxy] Procesando pago de ${monto} para socio {socio_id}...")
            
            # Simular generación de referencia
            timestamp = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
            referencia = f"PAY_{socio_id}_{timestamp}_{random.randint(1000, 9999)}"
            
            print(f"[PasarelaPagosProxy] Pago iniciado con referencia: {referencia}")
            return referencia
            
        except Exception as e:
            print(f"[PasarelaPagosProxy] Error al procesar pago: {str(e)}")
            return None
    
    def desconectar(self) -> None:
        """Cierra la conexión con la pasarela."""
        if self.conectado:
            print("[PasarelaPagosProxy] Cerrando conexión...")
            self.conectado = False
            print("[PasarelaPagosProxy] Conexión cerrada")

