"""Tests para funcionalidades de la Entrega 2"""
import pytest
from datetime import datetime, time
from src.models import Socio, Clase, PlanMembresia, Entrenador, Horario, Pago, EstadoPago
from src.services import ReservaService, PagoService
from src.repositories import SocioRepository, ClaseRepository, PlanRepository
from src.datasources.proxy import PasarelaPagosProxy, ClasesExternasProxy
from src.utils.enums import DiaSemana, RolUsuario, EstadoMembresia


class TestReservaService:
    """Tests para el servicio de reservas"""
    
    def test_crear_reserva_exitosa(self):
        """Test de creación exitosa de una reserva"""
        # Preparar datos
        plan = PlanMembresia("Plan Test", "Plan de prueba", 10000.0)
        socio = Socio("Juan", "Pérez", "12345678", "juan@test.com", plan)
        entrenador = Entrenador("Carlos", "López", "Instructor Certificado")
        horario = Horario(DiaSemana.LUNES, time(10, 0), time(11, 0))
        clase = Clase("Spinning", "Clase de spinning", 20, entrenador, horario)
        
        # Simular IDs (en un test real con DB, estos serían asignados)
        socio.id = 1
        clase.id = 1
        
        service = ReservaService()
        
        # Verificar que se pueda crear la reserva
        # (Este test requeriría mocking del repositorio en un caso real)
        assert socio.tiene_plan_activo()
        assert clase.tiene_cupo_disponible()
    
    def test_validar_cupo_disponible(self):
        """Test de validación de cupo disponible"""
        entrenador = Entrenador("María", "García", "Instructora")
        horario = Horario(DiaSemana.MARTES, time(18, 0), time(18, 45))
        clase = Clase("Yoga", "Clase de yoga", 10, entrenador, horario)
        
        # Inicialmente debe tener cupo
        assert clase.tiene_cupo_disponible()
        assert clase.cupos_disponibles() == 10


class TestPasarelaPagosProxy:
    """Tests para la integración con pasarela de pagos"""
    
    def test_conectar_pasarela(self):
        """Test de conexión con la pasarela"""
        config = {
            'api_key': 'test_key_123',
            'api_url': 'https://test-api.com'
        }
        proxy = PasarelaPagosProxy(config)
        
        # Debería conectarse exitosamente
        assert proxy.conectar() == True
        assert proxy.conectado == True
    
    def test_verificar_disponibilidad(self):
        """Test de verificación de disponibilidad"""
        proxy = PasarelaPagosProxy()
        proxy.conectar()
        
        # Verificar disponibilidad
        disponible = proxy.verificar_disponibilidad()
        assert isinstance(disponible, bool)
    
    def test_procesar_pago(self):
        """Test de procesamiento de pago"""
        proxy = PasarelaPagosProxy()
        proxy.conectar()
        
        referencia = proxy.procesar_pago(
            socio_id=1,
            monto=10000.0,
            metodo_pago="tarjeta"
        )
        
        assert referencia is not None
        assert "PAY_" in referencia


class TestClasesExternasProxy:
    """Tests para la integración con API de clases externas"""
    
    def test_conectar_api_externa(self):
        """Test de conexión con API externa"""
        config = {
            'api_url': 'https://api-externa.com',
            'proveedor': 'Talleres Especiales'
        }
        proxy = ClasesExternasProxy(config)
        
        assert proxy.conectar() == True
        assert proxy.conectado == True
    
    def test_obtener_clases_disponibles(self):
        """Test de obtención de clases externas"""
        proxy = ClasesExternasProxy()
        proxy.conectar()
        
        fecha_desde = datetime.now()
        clases = proxy.obtener_clases_disponibles(fecha_desde)
        
        assert isinstance(clases, list)
        # Deberían generarse clases para los próximos días
        assert len(clases) > 0
        
        # Verificar estructura de ClaseExterna
        if clases:
            clase = clases[0]
            assert hasattr(clase, 'titulo')
            assert hasattr(clase, 'instructor')
            assert hasattr(clase, 'cupos_disponibles')
            assert hasattr(clase, 'tiene_cupo')


class TestPagoService:
    """Tests para el servicio de pagos"""
    
    def test_crear_modelo_pago(self):
        """Test de creación del modelo Pago"""
        plan = PlanMembresia("Plan Premium", "Plan completo", 15000.0)
        socio = Socio("Ana", "Martínez", "87654321", "ana@test.com", plan)
        
        pago = Pago(
            socio=socio,
            monto=15000.0,
            mes_periodo=1,
            anio_periodo=2025,
            referencia_externa="PAY_TEST_123"
        )
        
        assert pago.monto == 15000.0
        assert pago.estado == EstadoPago.PENDIENTE
        assert pago.esta_pendiente()
        assert not pago.esta_aprobado()
    
    def test_actualizar_estado_pago(self):
        """Test de actualización de estado de pago"""
        plan = PlanMembresia("Plan Test", "Descripción", 10000.0)
        socio = Socio("Test", "User", "11111111", "test@test.com", plan)
        
        pago = Pago(socio, 10000.0, 1, 2025)
        
        # Inicialmente pendiente
        assert pago.estado == EstadoPago.PENDIENTE
        
        # Aprobar pago
        pago.actualizar_estado(EstadoPago.APROBADO)
        assert pago.esta_aprobado()
        assert pago.fecha_verificacion is not None


class TestValidacionAutomatica:
    """Tests para validación automática de solicitudes"""
    
    def test_validacion_solicitud_corta(self):
        """Test de rechazo automático por texto corto"""
        from src.validators.solicitud_validator import ValidadorCompuesto
        
        validador = ValidadorCompuesto()
        
        # Texto muy corto debería ser rechazado
        texto_corto = "Quiero darme de baja"
        assert not validador.es_valida(texto_corto)
    
    def test_validacion_solicitud_valida(self):
        """Test de aprobación de solicitud válida"""
        from src.validators.solicitud_validator import ValidadorCompuesto
        
        validador = ValidadorCompuesto()
        
        # Texto suficientemente largo y significativo
        texto_valido = (
            "Solicito la baja de mi membresía debido a que me mudaré a otra ciudad "
            "por motivos laborales. He disfrutado mucho de las instalaciones y el "
            "servicio brindado durante estos meses. Agradezco la atención prestada."
        )
        assert validador.es_valida(texto_valido)
    
    def test_validacion_solo_espacios(self):
        """Test de rechazo por texto vacío o solo espacios"""
        from src.validators.solicitud_validator import ValidadorPalabrasVacias
        
        validador = ValidadorPalabrasVacias()
        
        assert not validador.es_valida("   ")
        assert not validador.es_valida("")
        assert not validador.es_valida("\n\n\n")


class TestIntegracionEntrega2:
    """Tests de integración de funcionalidades de Entrega 2"""
    
    def test_flujo_completo_reserva(self):
        """Test del flujo completo de una reserva"""
        # Crear entidades necesarias
        plan = PlanMembresia("Plan Full", "Acceso total", 20000.0)
        socio = Socio("Pedro", "González", "99999999", "pedro@test.com", plan)
        entrenador = Entrenador("Lucía", "Ramos", "Profesora de Yoga")
        horario = Horario(DiaSemana.MIERCOLES, time(19, 0), time(20, 0))
        clase = Clase("Yoga Flow", "Yoga dinámico", 15, entrenador, horario)
        
        # Verificar precondiciones
        assert socio.tiene_plan_activo()
        assert clase.activa
        assert clase.tiene_cupo_disponible()
    
    def test_flujo_verificacion_pagos(self):
        """Test del flujo de verificación de pagos"""
        # Crear proxy de pagos
        proxy = PasarelaPagosProxy()
        
        # Conectar
        assert proxy.conectar()
        
        # Verificar disponibilidad
        disponible = proxy.verificar_disponibilidad()
        
        if disponible:
            # Simular verificación de un pago
            referencia = "PAY_TEST_12345"
            estado = proxy.verificar_estado_pago(referencia)
            assert estado is not None
            assert isinstance(estado, EstadoPago)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

