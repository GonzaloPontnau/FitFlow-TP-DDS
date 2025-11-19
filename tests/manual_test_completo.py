"""
Test Completo del TP FitFlow - Todas las Entregas
Valida funcionalidades de Entrega 1, 2 y 3
"""
import os
import sys
from datetime import time, datetime, timedelta

os.environ['DATABASE_URL'] = f'sqlite:///{os.getcwd()}/src/instance/fitflow_test.db'

from src.main import create_app
from src.config.database import db
from src.models import (
    Socio, Clase, Horario, Entrenador, PlanMembresia, 
    Reserva, ListaEspera, SolicitudBaja, Pago
)
from src.services.agregador_horarios_service import AgregadorHorariosService, ModoVisualizacion
from src.services.lista_espera_service import ListaEsperaService
from src.services.solicitud_baja_service import SolicitudBajaService
from src.utils.enums import DiaSemana, EstadoSolicitudBaja, EstadoMembresia, RolUsuario

class TestSuite:
    def __init__(self):
        self.app = None
        self.tests_passed = 0
        self.tests_failed = 0
        self.datos = {}
    
    def setup(self):
        """Inicializa la aplicación y base de datos"""
        print("\n" + "="*60)
        print("  SETUP: Inicializando aplicación y base de datos")
        print("="*60)
        
        self.app = create_app()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self._crear_datos_base()
        
        print("OK - Base de datos inicializada")
    
    def _crear_datos_base(self):
        """Crea datos base para las pruebas"""
        # Entrenador
        entrenador = Entrenador(
            nombre="Carlos",
            apellido="Martinez",
            email="carlos@fitflow.com",
            especialidad="Entrenamiento Funcional"
        )
        db.session.add(entrenador)
        
        # Planes de membresía
        plan_basico = PlanMembresia(
            titulo="Plan Básico",
            descripcion="Acceso a clases básicas",
            precio=5000.0
        )
        plan_premium = PlanMembresia(
            titulo="Plan Premium",
            descripcion="Acceso ilimitado a todas las clases",
            precio=15000.0
        )
        db.session.add_all([plan_basico, plan_premium])
        
        # Horarios
        horario_lunes = Horario(
            dia_semana=DiaSemana.LUNES,
            hora_inicio=time(18, 0),
            hora_fin=time(19, 0)
        )
        horario_miercoles = Horario(
            dia_semana=DiaSemana.MIERCOLES,
            hora_inicio=time(19, 0),
            hora_fin=time(20, 0)
        )
        horario_viernes = Horario(
            dia_semana=DiaSemana.VIERNES,
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0)
        )
        db.session.add_all([horario_lunes, horario_miercoles, horario_viernes])
        
        # Clases
        clase_funcional = Clase(
            titulo="Funcional Intenso",
            descripcion="Entrenamiento funcional de alta intensidad",
            cupo_maximo=15,
            entrenador=entrenador,
            horario=horario_lunes
        )
        clase_funcional.tiene_lista_espera = True
        
        clase_yoga = Clase(
            titulo="Yoga Integral",
            descripcion="Yoga para todos los niveles",
            cupo_maximo=20,
            entrenador=entrenador,
            horario=horario_miercoles
        )
        
        clase_crossfit = Clase(
            titulo="CrossFit",
            descripcion="Entrenamiento de alta intensidad",
            cupo_maximo=3,  # Cupo reducido para probar lista de espera
            entrenador=entrenador,
            horario=horario_viernes
        )
        clase_crossfit.tiene_lista_espera = True
        
        db.session.add_all([clase_funcional, clase_yoga, clase_crossfit])
        
        # Asociar clases a planes
        plan_basico.clases.extend([clase_funcional, clase_yoga])
        plan_premium.clases.extend([clase_funcional, clase_yoga, clase_crossfit])
        
        # Socios
        socio1 = Socio("Juan", "Perez", "11111111", "juan@email.com")
        socio1.plan_membresia = plan_basico
        socio1.rol = RolUsuario.SOCIO_REGISTRADO
        
        socio2 = Socio("Maria", "Lopez", "22222222", "maria@email.com")
        socio2.plan_membresia = plan_premium
        socio2.rol = RolUsuario.SOCIO_REGISTRADO
        
        socio3 = Socio("Pedro", "Garcia", "33333333", "pedro@email.com")
        socio3.plan_membresia = plan_premium
        socio3.rol = RolUsuario.SOCIO_REGISTRADO
        
        socio4 = Socio("Ana", "Rodriguez", "44444444", "ana@email.com")
        socio4.plan_membresia = plan_basico
        socio4.rol = RolUsuario.SOCIO_REGISTRADO
        socio4.estado_membresia = EstadoMembresia.ACTIVA
        
        socio5 = Socio("Luis", "Fernandez", "55555555", "luis@email.com")
        socio5.rol = RolUsuario.VISUALIZADOR
        
        db.session.add_all([socio1, socio2, socio3, socio4, socio5])
        
        db.session.commit()
        
        # Guardar IDs para usar en las pruebas
        self.datos = {
            'entrenador_id': entrenador.id,
            'plan_basico_id': plan_basico.id,
            'plan_premium_id': plan_premium.id,
            'clase_funcional_id': clase_funcional.id,
            'clase_yoga_id': clase_yoga.id,
            'clase_crossfit_id': clase_crossfit.id,
            'socio1_id': socio1.id,
            'socio2_id': socio2.id,
            'socio3_id': socio3.id,
            'socio4_id': socio4.id,
            'socio5_id': socio5.id,
        }
        
        print(f"OK - Datos base creados:")
        print(f"     Socios: {len([socio1, socio2, socio3, socio4, socio5])}")
        print(f"     Clases: {len([clase_funcional, clase_yoga, clase_crossfit])}")
        print(f"     Planes: {len([plan_basico, plan_premium])}")
    
    def test_entrega1_modelo_dominio(self):
        """ENTREGA 1: Validar modelo de dominio y relaciones"""
        print("\n" + "-"*60)
        print("TEST ENTREGA 1: Modelo de Dominio")
        print("-"*60)
        
        with self.app.app_context():
            try:
                # Test 1.1: Verificar socios
                socios = Socio.query.all()
                assert len(socios) == 5, f"Expected 5 socios, got {len(socios)}"
                print("OK - 1.1: Socios creados correctamente")
                
                # Test 1.2: Verificar clases
                clases = Clase.query.all()
                assert len(clases) == 3, f"Expected 3 clases, got {len(clases)}"
                print("OK - 1.2: Clases creadas correctamente")
                
                # Test 1.3: Verificar planes
                planes = PlanMembresia.query.all()
                assert len(planes) == 2, f"Expected 2 planes, got {len(planes)}"
                print("OK - 1.3: Planes creados correctamente")
                
                # Test 1.4: Relación Socio-Plan
                socio = Socio.query.get(self.datos['socio1_id'])
                assert socio.plan_membresia is not None, "Socio should have a plan"
                assert socio.plan_membresia.titulo == "Plan Básico"
                print(f"OK - 1.4: Relación Socio-Plan: {socio.nombre} tiene {socio.plan_membresia.titulo}")
                
                # Test 1.5: Relación Clase-Entrenador
                clase = Clase.query.get(self.datos['clase_funcional_id'])
                assert clase.entrenador is not None, "Clase should have entrenador"
                assert clase.entrenador.nombre == "Carlos"
                print(f"OK - 1.5: Relación Clase-Entrenador: {clase.titulo} con {clase.entrenador.nombre}")
                
                # Test 1.6: Relación Plan-Clases (Many-to-Many)
                plan_basico = PlanMembresia.query.get(self.datos['plan_basico_id'])
                assert len(plan_basico.clases) == 2, f"Plan Básico should have 2 clases"
                print(f"OK - 1.6: Plan-Clases: Plan Básico tiene {len(plan_basico.clases)} clases")
                
                # Test 1.7: Roles de usuario
                socio_reg = Socio.query.get(self.datos['socio1_id'])
                visualizador = Socio.query.get(self.datos['socio5_id'])
                assert socio_reg.rol == RolUsuario.SOCIO_REGISTRADO
                assert visualizador.rol == RolUsuario.VISUALIZADOR
                print("OK - 1.7: Roles de usuario asignados correctamente")
                
                self.tests_passed += 7
                print("\nENTREGA 1: TODOS LOS TESTS PASARON (7/7)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def test_entrega2_reservas_y_pagos(self):
        """ENTREGA 2: Sistema de reservas y pagos"""
        print("\n" + "-"*60)
        print("TEST ENTREGA 2: Reservas y Pagos")
        print("-"*60)
        
        with self.app.app_context():
            try:
                socio = Socio.query.get(self.datos['socio1_id'])
                clase = Clase.query.get(self.datos['clase_funcional_id'])
                
                # Test 2.1: Crear reserva
                reserva = Reserva(socio=socio, clase=clase)
                db.session.add(reserva)
                db.session.commit()
                
                assert reserva.id is not None, "Reserva should have ID"
                assert reserva.confirmada == True, "Reserva should be confirmed"
                print(f"OK - 2.1: Reserva creada (ID: {reserva.id})")
                
                # Test 2.2: Verificar cupos disponibles
                cupos_disponibles = clase.cupos_disponibles()
                assert cupos_disponibles == 14, f"Expected 14 cupos, got {cupos_disponibles}"
                print(f"OK - 2.2: Cupos disponibles: {cupos_disponibles}/{clase.cupo_maximo}")
                
                # Test 2.3: Relación Socio-Reservas
                socio_reservas = Socio.query.get(self.datos['socio1_id'])
                assert len(socio_reservas.reservas) == 1, "Socio should have 1 reserva"
                print(f"OK - 2.3: Socio tiene {len(socio_reservas.reservas)} reserva(s)")
                
                # Test 2.4: Cancelar reserva
                reserva.cancelar()
                db.session.commit()
                assert reserva.confirmada == False, "Reserva should be cancelled"
                assert reserva.fecha_cancelacion is not None
                print("OK - 2.4: Reserva cancelada correctamente")
                
                # Test 2.5: Crear pago
                pago = Pago(
                    socio=socio,
                    monto=5000.0,
                    mes_periodo=11,
                    anio_periodo=2025
                )
                db.session.add(pago)
                db.session.commit()
                
                assert pago.id is not None, "Pago should have ID"
                print(f"OK - 2.5: Pago registrado (ID: {pago.id}, Monto: ${pago.monto})")
                
                # Test 2.6: Verificar relación Socio-Pagos
                socio_pagos = Socio.query.get(self.datos['socio1_id'])
                assert len(socio_pagos.pagos) == 1, "Socio should have 1 pago"
                print(f"OK - 2.6: Socio tiene {len(socio_pagos.pagos)} pago(s)")
                
                # Test 2.7: Crear múltiples reservas
                socio2 = Socio.query.get(self.datos['socio2_id'])
                clase_yoga = Clase.query.get(self.datos['clase_yoga_id'])
                
                reserva2 = Reserva(socio=socio2, clase=clase_yoga)
                reserva3 = Reserva(socio=socio2, clase=clase)
                db.session.add_all([reserva2, reserva3])
                db.session.commit()
                
                total_reservas = Reserva.query.count()
                assert total_reservas == 3, f"Expected 3 reservas, got {total_reservas}"
                print(f"OK - 2.7: Total de reservas en sistema: {total_reservas}")
                
                self.tests_passed += 7
                print("\nENTREGA 2: TODOS LOS TESTS PASARON (7/7)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def test_entrega3_calendario_agregador(self):
        """ENTREGA 3A: Calendario Agregador"""
        print("\n" + "-"*60)
        print("TEST ENTREGA 3A: Calendario Agregador")
        print("-"*60)
        
        with self.app.app_context():
            try:
                servicio = AgregadorHorariosService()
                
                # Test 3.1: Obtener calendario modo NORMAL
                calendario = servicio.obtener_calendario_consolidado(
                    modo=ModoVisualizacion.NORMAL
                )
                assert len(calendario) > 0, "Calendario should have events"
                print(f"OK - 3.1: Calendario NORMAL generado ({len(calendario)} eventos)")
                
                # Test 3.2: Verificar eventos internos
                eventos_internos = [e for e in calendario if e.tipo == 'interna']
                assert len(eventos_internos) > 0, "Should have internal events"
                print(f"OK - 3.2: Eventos internos: {len(eventos_internos)}")
                
                # Test 3.3: Verificar eventos externos
                eventos_externos = [e for e in calendario if e.tipo == 'externa']
                print(f"OK - 3.3: Eventos externos: {len(eventos_externos)}")
                
                # Test 3.4: Calendario modo OCUPADO
                calendario_ocupado = servicio.obtener_calendario_consolidado(
                    modo=ModoVisualizacion.OCUPADO
                )
                print(f"OK - 3.4: Calendario OCUPADO generado ({len(calendario_ocupado)} eventos)")
                
                # Test 3.5: Filtrado por fechas
                hoy = datetime.now()
                semana = hoy + timedelta(days=7)
                calendario_filtrado = servicio.obtener_calendario_consolidado(
                    fecha_desde=hoy.date(),
                    fecha_hasta=semana.date()
                )
                print(f"OK - 3.5: Calendario filtrado por fechas ({len(calendario_filtrado)} eventos)")
                
                # Test 3.6: Verificar estructura de eventos
                if calendario:
                    evento = calendario[0]
                    assert hasattr(evento, 'titulo'), "Evento should have titulo"
                    assert hasattr(evento, 'fecha'), "Evento should have fecha"
                    assert hasattr(evento, 'hora_inicio'), "Evento should have hora_inicio"
                    assert hasattr(evento, 'cupo_maximo'), "Evento should have cupo_maximo"
                    print(f"OK - 3.6: Estructura de evento validada")
                    print(f"         Ejemplo: {evento.titulo} - {evento.fecha} {evento.hora_inicio}")
                
                self.tests_passed += 6
                print("\nENTREGA 3A: TODOS LOS TESTS PASARON (6/6)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def test_entrega3_lista_espera(self):
        """ENTREGA 3B: Sistema de Listas de Espera"""
        print("\n" + "-"*60)
        print("TEST ENTREGA 3B: Listas de Espera")
        print("-"*60)
        
        with self.app.app_context():
            try:
                servicio = ListaEsperaService()
                
                # Preparar: llenar cupos de clase CrossFit (cupo máximo: 3)
                clase = Clase.query.get(self.datos['clase_crossfit_id'])
                socio1 = Socio.query.get(self.datos['socio1_id'])
                socio2 = Socio.query.get(self.datos['socio2_id'])
                socio3 = Socio.query.get(self.datos['socio3_id'])
                socio4 = Socio.query.get(self.datos['socio4_id'])
                
                # Llenar cupos
                r1 = Reserva(socio=socio1, clase=clase)
                r2 = Reserva(socio=socio2, clase=clase)
                r3 = Reserva(socio=socio3, clase=clase)
                db.session.add_all([r1, r2, r3])
                db.session.commit()
                
                print(f"PREPARACION: Clase llena ({clase.cupos_disponibles()}/{clase.cupo_maximo})")
                
                # Test 3.7: Inscribir en lista de espera
                entrada = servicio.inscribir_en_lista_espera(socio4, clase)
                assert entrada is not None, "Should create lista espera entry"
                assert entrada.posicion == 1, f"Expected position 1, got {entrada.posicion}"
                print(f"OK - 3.7: Socio inscrito en lista de espera (posición {entrada.posicion})")
                
                # Test 3.8: Verificar entrada en DB
                entrada_db = ListaEspera.query.filter_by(
                    socio_id=socio4.id, 
                    clase_id=clase.id
                ).first()
                assert entrada_db is not None, "Entry should exist in DB"
                assert entrada_db.activo == True
                print("OK - 3.8: Entrada guardada en base de datos")
                
                # Test 3.9: Liberar cupo y notificar
                db.session.delete(r1)
                db.session.commit()
                print(f"ACCION: Cupo liberado ({clase.cupos_disponibles()}/{clase.cupo_maximo})")
                
                notificado = servicio.notificar_siguiente_en_lista(clase)
                assert notificado is not None, "Should notify next in line"
                assert notificado.notificado == True
                assert notificado.fecha_notificacion is not None
                print(f"OK - 3.9: Socio {notificado.socio_id} notificado")
                
                # Test 3.10: Confirmar lugar
                confirmado = servicio.confirmar_lugar(socio4, clase)
                assert confirmado is not None, "Should create reservation"
                print(f"OK - 3.10: Lugar confirmado (Reserva ID: {confirmado.id})")
                
                # Test 3.11: Verificar entrada desactivada
                entrada_final = ListaEspera.query.get(entrada.id)
                assert entrada_final.confirmado == True
                assert entrada_final.activo == False
                print("OK - 3.11: Entrada de lista de espera desactivada")
                
                # Test 3.12: Verificar nueva reserva
                nueva_reserva = Reserva.query.filter_by(
                    socio_id=socio4.id,
                    clase_id=clase.id
                ).first()
                assert nueva_reserva is not None, "Should create reservation"
                assert nueva_reserva.confirmada == True
                print(f"OK - 3.12: Nueva reserva creada y confirmada")
                
                # Test 3.13: Verificar cupos actualizados
                cupos = clase.cupos_disponibles()
                assert cupos == 0, f"Expected 0 cupos, got {cupos}"
                print(f"OK - 3.13: Cupos actualizados: {cupos}/{clase.cupo_maximo}")
                
                self.tests_passed += 7
                print("\nENTREGA 3B: TODOS LOS TESTS PASARON (7/7)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def test_entrega3_solicitudes_baja(self):
        """ENTREGA 3C: Sistema de Solicitudes de Baja"""
        print("\n" + "-"*60)
        print("TEST ENTREGA 3C: Solicitudes de Baja")
        print("-"*60)
        
        with self.app.app_context():
            try:
                servicio = SolicitudBajaService()
                socio = Socio.query.get(self.datos['socio2_id'])
                
                # Test 3.14: Crear solicitud
                justificacion = "Me mudo a otra ciudad por trabajo y no podre seguir asistiendo al gimnasio. He disfrutado mucho las clases pero lamentablemente debo cancelar mi membresia por este motivo de fuerza mayor."
                solicitud = servicio.crear_solicitud(
                    socio_id=socio.id,
                    justificacion=justificacion
                )
                assert solicitud is not None, "Should create solicitud"
                assert solicitud.estado == EstadoSolicitudBaja.PENDIENTE
                print(f"OK - 3.14: Solicitud creada (ID: {solicitud.id})")
                
                # Test 3.15: Verificar estado inicial
                assert solicitud.fecha_solicitud is not None
                assert solicitud.fecha_resolucion is None
                print("OK - 3.15: Estado PENDIENTE con fecha de solicitud")
                
                # Test 3.16: Listar solicitudes
                solicitudes = SolicitudBaja.query.all()
                assert len(solicitudes) > 0, "Should have solicitudes"
                print(f"OK - 3.16: Total solicitudes: {len(solicitudes)}")
                
                # Test 3.17: Aprobar solicitud
                aprobada = servicio.aprobar_solicitud(solicitud.id)
                assert aprobada.estado == EstadoSolicitudBaja.APROBADA
                assert aprobada.fecha_resolucion is not None
                print(f"OK - 3.17: Solicitud APROBADA")
                
                # Test 3.18: Crear y rechazar otra solicitud
                socio3 = Socio.query.get(self.datos['socio3_id'])
                solicitud2 = servicio.crear_solicitud(
                    socio_id=socio3.id,
                    justificacion="Motivo personal suficientemente largo para cumplir con el requisito minimo de caracteres establecido en el sistema para poder procesar correctamente la solicitud de baja del gimnasio FitFlow"
                )
                
                rechazada = servicio.rechazar_solicitud(
                    solicitud2.id,
                    "Tiene pagos pendientes"
                )
                assert rechazada.estado == EstadoSolicitudBaja.RECHAZADA
                assert rechazada.comentario_admin == "Tiene pagos pendientes"
                print(f"OK - 3.18: Solicitud RECHAZADA con motivo")
                
                # Test 3.19: Filtrar por estado
                pendientes = [s for s in SolicitudBaja.query.all() if s.estado == EstadoSolicitudBaja.PENDIENTE]
                aprobadas = [s for s in SolicitudBaja.query.all() if s.estado == EstadoSolicitudBaja.APROBADA]
                rechazadas = [s for s in SolicitudBaja.query.all() if s.estado == EstadoSolicitudBaja.RECHAZADA]
                print(f"OK - 3.19: Filtrado por estado:")
                print(f"         Pendientes: {len(pendientes)}")
                print(f"         Aprobadas: {len(aprobadas)}")
                print(f"         Rechazadas: {len(rechazadas)}")
                
                # Test 3.20: Obtener por socio
                solicitudes_socio = servicio.obtener_solicitudes_socio(socio.id)
                assert len(solicitudes_socio) > 0, "Socio should have solicitudes"
                print(f"OK - 3.20: Solicitudes del socio: {len(solicitudes_socio)}")
                
                self.tests_passed += 7
                print("\nENTREGA 3C: TODOS LOS TESTS PASARON (7/7)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def test_integracion_completa(self):
        """TEST DE INTEGRACION: Flujo completo de usuario"""
        print("\n" + "-"*60)
        print("TEST INTEGRACION: Flujo Completo de Usuario")
        print("-"*60)
        
        with self.app.app_context():
            try:
                # Simular usuario nuevo
                nuevo_socio = Socio("Roberto", "Sanchez", "99999999", "roberto@email.com")
                nuevo_socio.rol = RolUsuario.SOCIO_REGISTRADO
                db.session.add(nuevo_socio)
                db.session.commit()
                
                # Asignar plan
                plan = PlanMembresia.query.get(self.datos['plan_premium_id'])
                nuevo_socio.plan_membresia = plan
                db.session.commit()
                print(f"OK - I.1: Nuevo socio registrado con {plan.titulo}")
                
                # Registrar pago
                pago = Pago(
                    socio=nuevo_socio,
                    monto=plan.precio,
                    mes_periodo=11,
                    anio_periodo=2025
                )
                db.session.add(pago)
                db.session.commit()
                print(f"OK - I.2: Pago registrado: ${pago.monto}")
                
                # Hacer reserva
                clase = Clase.query.get(self.datos['clase_yoga_id'])
                reserva = Reserva(socio=nuevo_socio, clase=clase)
                db.session.add(reserva)
                db.session.commit()
                print(f"OK - I.3: Reserva en {clase.titulo}")
                
                # Ver calendario
                servicio_calendario = AgregadorHorariosService()
                calendario = servicio_calendario.obtener_calendario_consolidado()
                print(f"OK - I.4: Consultó calendario ({len(calendario)} eventos)")
                
                # Cancelar reserva
                reserva.cancelar()
                db.session.commit()
                print(f"OK - I.5: Reserva cancelada")
                
                # Solicitar baja
                servicio_baja = SolicitudBajaService()
                solicitud = servicio_baja.crear_solicitud(
                    socio_id=nuevo_socio.id,
                    justificacion="Debido a un cambio de residencia y nuevas responsabilidades laborales que me impiden asistir regularmente al gimnasio, solicito la baja de mi membresia. Agradezco los servicios prestados durante este tiempo."
                )
                print(f"OK - I.6: Solicitud de baja creada (ID: {solicitud.id})")
                
                self.tests_passed += 6
                print("\nINTEGRACION: TODOS LOS TESTS PASARON (6/6)")
                
            except AssertionError as e:
                self.tests_failed += 1
                print(f"FAIL - {str(e)}")
                raise
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("\n" + "="*60)
        print("  TEST COMPLETO - TODAS LAS ENTREGAS DEL TP")
        print("  FitFlow - Sistema de Gestión de Gimnasio")
        print("="*60)
        
        start_time = datetime.now()
        
        try:
            self.setup()
            self.test_entrega1_modelo_dominio()
            self.test_entrega2_reservas_y_pagos()
            self.test_entrega3_calendario_agregador()
            self.test_entrega3_lista_espera()
            self.test_entrega3_solicitudes_baja()
            self.test_integracion_completa()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*60)
            print("  RESUMEN FINAL")
            print("="*60)
            print(f"\nTests ejecutados: {self.tests_passed + self.tests_failed}")
            print(f"Tests exitosos:   {self.tests_passed}")
            print(f"Tests fallidos:   {self.tests_failed}")
            print(f"Tiempo total:     {duration:.2f} segundos")
            
            if self.tests_failed == 0:
                print("\n" + "="*60)
                print("  TODOS LOS TESTS PASARON EXITOSAMENTE")
                print("="*60)
                print("\nValidaciones completadas:")
                print("  [x] ENTREGA 1: Modelo de dominio (7 tests)")
                print("  [x] ENTREGA 2: Reservas y pagos (7 tests)")
                print("  [x] ENTREGA 3A: Calendario agregador (6 tests)")
                print("  [x] ENTREGA 3B: Listas de espera (7 tests)")
                print("  [x] ENTREGA 3C: Solicitudes de baja (7 tests)")
                print("  [x] INTEGRACION: Flujo completo (6 tests)")
                print("\nTotal: 40 tests exitosos")
                print("\n" + "="*60)
                return 0
            else:
                print("\nAlgunos tests fallaron. Revisar logs arriba.")
                return 1
                
        except Exception as e:
            print(f"\n\nERROR CRITICO: {str(e)}")
            import traceback
            traceback.print_exc()
            return 1

if __name__ == "__main__":
    suite = TestSuite()
    exit_code = suite.run_all_tests()
    sys.exit(exit_code)
