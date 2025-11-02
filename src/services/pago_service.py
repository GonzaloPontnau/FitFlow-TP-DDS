"""Servicio de gestión de pagos"""
from typing import List, Dict, Optional
from datetime import datetime
from src.repositories.pago_repository import PagoRepository
from src.repositories.socio_repository import SocioRepository
from src.models.pago import Pago, EstadoPago
from src.datasources.proxy.pasarela_pagos_proxy import PasarelaPagosProxy


class PagoService:
    """
    Servicio para la gestión de pagos y verificación con pasarela externa.
    
    Gestiona la creación de pagos, verificación de estados con la pasarela
    externa y actualización del estado de membresías según los pagos.
    """
    
    def __init__(self, config: Dict[str, any] = None):
        """
        Inicializa el servicio de pagos.
        
        Args:
            config: Configuración para la pasarela de pagos
        """
        self.pago_repository = PagoRepository()
        self.socio_repository = SocioRepository()
        self.pasarela_proxy = PasarelaPagosProxy(config)
    
    def registrar_pago(self, socio_id: int, mes_periodo: int, 
                       anio_periodo: int) -> Dict[str, any]:
        """
        Registra un nuevo pago para un socio.
        
        Args:
            socio_id: ID del socio
            mes_periodo: Mes del período a pagar
            anio_periodo: Año del período a pagar
            
        Returns:
            Dict con el resultado de la operación
        """
        # Validar que el socio existe
        socio = self.socio_repository.find_by_id(socio_id)
        if not socio:
            return {
                'success': False,
                'pago': None,
                'message': f'El socio con ID {socio_id} no existe'
            }
        
        # Validar que el socio tenga un plan
        if not socio.plan_membresia:
            return {
                'success': False,
                'pago': None,
                'message': 'El socio no tiene un plan de membresía asignado'
            }
        
        # Verificar si ya existe un pago para este período
        pago_existente = self.pago_repository.find_pagos_socio_periodo(
            socio_id, mes_periodo, anio_periodo
        )
        if pago_existente:
            return {
                'success': False,
                'pago': pago_existente,
                'message': f'Ya existe un pago para el período {mes_periodo}/{anio_periodo}'
            }
        
        # Conectar con la pasarela
        if not self.pasarela_proxy.conectar():
            return {
                'success': False,
                'pago': None,
                'message': 'Error al conectar con la pasarela de pagos'
            }
        
        # Procesar el pago en la pasarela
        monto = socio.plan_membresia.precio
        referencia = self.pasarela_proxy.procesar_pago(socio_id, monto)
        
        if not referencia:
            return {
                'success': False,
                'pago': None,
                'message': 'Error al procesar el pago en la pasarela'
            }
        
        # Crear registro de pago
        pago = Pago(
            socio=socio,
            monto=monto,
            mes_periodo=mes_periodo,
            anio_periodo=anio_periodo,
            referencia_externa=referencia
        )
        
        pago_guardado = self.pago_repository.save(pago)
        
        return {
            'success': True,
            'pago': pago_guardado,
            'message': f'Pago registrado exitosamente. Referencia: {referencia}'
        }
    
    def verificar_pagos_pendientes(self) -> Dict[str, any]:
        """
        Verifica el estado de todos los pagos pendientes con la pasarela.
        
        Este método debe ejecutarse periódicamente (ej. una vez al día)
        para actualizar el estado de los pagos.
        
        Returns:
            Dict con estadísticas de la verificación
        """
        print("\n=== Iniciando verificación de pagos pendientes ===")
        
        # Conectar con la pasarela
        if not self.pasarela_proxy.conectar():
            return {
                'success': False,
                'message': 'Error al conectar con la pasarela de pagos',
                'verificados': 0,
                'aprobados': 0,
                'rechazados': 0
            }
        
        # Verificar disponibilidad
        if not self.pasarela_proxy.verificar_disponibilidad():
            return {
                'success': False,
                'message': 'La pasarela de pagos no está disponible',
                'verificados': 0,
                'aprobados': 0,
                'rechazados': 0
            }
        
        # Obtener pagos pendientes
        pagos_pendientes = self.pago_repository.find_pagos_pendientes()
        print(f"Pagos pendientes encontrados: {len(pagos_pendientes)}")
        
        if not pagos_pendientes:
            return {
                'success': True,
                'message': 'No hay pagos pendientes de verificación',
                'verificados': 0,
                'aprobados': 0,
                'rechazados': 0
            }
        
        # Obtener referencias para verificar en lote
        referencias = [p.referencia_externa for p in pagos_pendientes 
                      if p.referencia_externa]
        
        # Verificar estados en lote
        estados = self.pasarela_proxy.verificar_estados_lote(referencias)
        
        # Actualizar estados de los pagos
        verificados = 0
        aprobados = 0
        rechazados = 0
        
        for pago in pagos_pendientes:
            if pago.referencia_externa in estados:
                nuevo_estado = estados[pago.referencia_externa]
                pago.actualizar_estado(nuevo_estado)
                self.pago_repository.save(pago)
                
                verificados += 1
                if nuevo_estado == EstadoPago.APROBADO:
                    aprobados += 1
                    # Reactivar membresía si estaba suspendida
                    self._actualizar_estado_membresia(pago)
                elif nuevo_estado == EstadoPago.RECHAZADO:
                    rechazados += 1
                    print(f"⚠️  Pago rechazado: {pago.referencia_externa}")
        
        self.pasarela_proxy.desconectar()
        
        print(f"\n=== Verificación completada ===")
        print(f"Total verificados: {verificados}")
        print(f"Aprobados: {aprobados}")
        print(f"Rechazados: {rechazados}")
        
        return {
            'success': True,
            'message': f'Verificación completada: {verificados} pagos procesados',
            'verificados': verificados,
            'aprobados': aprobados,
            'rechazados': rechazados
        }
    
    def listar_pagos_socio(self, socio_id: int) -> List[Pago]:
        """
        Lista todos los pagos de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de pagos del socio
        """
        return self.pago_repository.find_by_socio(socio_id)
    
    def obtener_pago_por_referencia(self, referencia: str) -> Optional[Pago]:
        """
        Obtiene un pago por su referencia externa.
        
        Args:
            referencia: Referencia externa del pago
            
        Returns:
            Objeto Pago o None si no existe
        """
        return self.pago_repository.find_by_referencia_externa(referencia)
    
    def _actualizar_estado_membresia(self, pago: Pago) -> None:
        """
        Actualiza el estado de membresía del socio según el pago.
        
        Args:
            pago: Pago aprobado
        """
        from src.utils.enums import EstadoMembresia
        
        socio = pago.socio
        if pago.esta_aprobado():
            # Si el pago fue aprobado, activar la membresía
            if socio.estado_membresia == EstadoMembresia.SUSPENDIDA:
                socio.estado_membresia = EstadoMembresia.ACTIVA
                self.socio_repository.save(socio)
                print(f"✓ Membresía reactivada para socio {socio.nombre_completo}")

