import sys
import os
from datetime import datetime, date, time, timedelta

# Asegurar que podemos importar modulos de src
sys.path.append(os.getcwd())

from src.main import create_app
from src.config.database import db
from src.services.reserva_service import ReservaService
from src.services.lista_espera_service import ListaEsperaService
from src.services.solicitud_baja_service import SolicitudBajaService
from src.models.clase import Clase
from src.models.socio import Socio
from src.models.plan_membresia import PlanMembresia
from src.models.entrenador import Entrenador
from src.models.horario import Horario, DiaSemana
from src.exceptions.base_exceptions import BusinessException, ValidationException

# Inicializar app
app = create_app()

def log_test(name, result, message=""):
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status} | {name} | {message}")

def run_verification():
    print("=== INICIANDO VERIFICACIÓN DE FLUJOS CRÍTICOS Y VALORES LÍMITE ===\n")
    
    with app.app_context():
        # --- SETUP: Crear datos de prueba específicos ---
        prefix = f"TEST_{datetime.now().strftime('%H%M%S')}"
        
        # 1. Crear Plan
        plan = PlanMembresia(titulo=f"{prefix}_Plan", descripcion="Plan de Prueba", precio=1000)
        db.session.add(plan)
        
        # 2. Crear Entrenador y Horario
        entrenador = Entrenador(nombre=f"{prefix}_Entrenador", apellido="Test", email=f"ent_{prefix}@test.com", especialidad="Test")
        horario = Horario(dia_semana=DiaSemana.LUNES, hora_inicio=time(10,0), hora_fin=time(11,0))
        db.session.add(entrenador)
        db.session.add(horario)
        db.session.commit()
        
        # 3. Crear Clase con CUPO LIMITADO (Boundary: 1)
        clase_limite = Clase(
            titulo=f"{prefix}_ClaseLimite", 
            descripcion="Clase con cupo 1", 
            cupo_maximo=1,
            entrenador=entrenador,
            horario=horario
        )
        clase_limite.tiene_lista_espera = True # Habilitar lista de espera
        db.session.add(clase_limite)
        
        # 4. Crear Socios (Socio 1 y Socio 2)
        # Nota: Socio no tiene telefono ni fecha_fin en init, el plan se asigna directamente
        socio1 = Socio(nombre=f"{prefix}_Socio1", apellido="Test", dni=f"111{prefix}", email=f"s1_{prefix}@test.com", plan_membresia=plan)
        socio2 = Socio(nombre=f"{prefix}_Socio2", apellido="Test", dni=f"222{prefix}", email=f"s2_{prefix}@test.com", plan_membresia=plan)
        socio3 = Socio(nombre=f"{prefix}_Socio3", apellido="Test", dni=f"333{prefix}", email=f"s3_{prefix}@test.com", plan_membresia=plan)
        
        db.session.add_all([socio1, socio2, socio3])
        db.session.commit()
        
        # Vincular clase al plan (para que puedan reservarla)
        if clase_limite not in plan.clases:
            plan.clases.append(clase_limite)
        db.session.commit()
        
        reserva_service = ReservaService()
        lista_espera_service = ListaEsperaService()
        solicitud_baja_service = SolicitudBajaService()

        print("--- SETUP COMPLETADO ---\n")

        # === TEST 1: RESERVA EXITOSA (Happy Path) ===
        try:
            resultado = reserva_service.crear_reserva(socio1.id, clase_limite.id)
            log_test("Reserva Exitosa", resultado['success'], resultado.get('message', ''))
            reserva_id_s1 = resultado['reserva'].id
        except Exception as e:
            log_test("Reserva Exitosa", False, str(e))

        # === TEST 2: RESERVA DUPLICADA (Boundary: Mismo socio, misma clase) ===
        try:
            resultado = reserva_service.crear_reserva(socio1.id, clase_limite.id)
            # Esperamos success=False
            log_test("Bloqueo Duplicados", not resultado['success'], f"Correctamente rechazado: {resultado.get('message')}")
        except Exception as e:
            log_test("Bloqueo Duplicados", False, str(e))

        # === TEST 3: CUPO COMPLETO (Boundary: Max Capacity Reached) ===
        try:
            # Socio 2 intenta reservar, pero el cupo es 1 y lo tiene Socio 1
            resultado = reserva_service.crear_reserva(socio2.id, clase_limite.id)
            log_test("Control de Cupo Máximo", not resultado['success'], f"Correctamente rechazado por cupo: {resultado.get('message')}")
        except Exception as e:
            log_test("Control de Cupo Máximo", False, str(e))

        # === TEST 4: LISTA DE ESPERA - INSCRIPCIÓN ===
        try:
            # Socio 2 se inscribe en lista de espera
            entrada = lista_espera_service.inscribir_en_lista_espera(socio2, clase_limite)
            posicion = entrada.posicion if entrada else 0
            log_test("Inscripción Lista Espera", entrada is not None, f"Socio 2 en posición {posicion}")
        except Exception as e:
            log_test("Inscripción Lista Espera", False, str(e))
            
        # === TEST 5: LISTA DE ESPERA - MULTIPLE INSCRIPCIÓN (Boundary) ===
        try:
            # Socio 2 intenta inscribirse de nuevo (ValidationException esperado)
            try:
                lista_espera_service.inscribir_en_lista_espera(socio2, clase_limite)
                log_test("Bloqueo Duplicado Lista Espera", False, "Debería haber fallado")
            except ValidationException as e:
                log_test("Bloqueo Duplicado Lista Espera", True, f"Correctamente rechazado (ValidationException)")
            except BusinessException as e:
                 log_test("Bloqueo Duplicado Lista Espera", True, f"Correctamente rechazado (BusinessException)")
        except Exception as e:
            log_test("Bloqueo Duplicado Lista Espera", False, f"Error inesperado: {type(e)}")

        # === TEST 6: CONFIRMACIÓN LISTA DE ESPERA (Flow Completo) ===
        # Paso A: Socio 1 cancela reserva -> Se libera cupo
        try:
            reserva_service.cancelar_reserva(reserva_id_s1)
            # Forzar procesamiento de notificaciones
            notificadas = lista_espera_service.procesar_liberaciones_cupos()
            log_test("Procesamiento Liberación Cupos", notificadas > 0, "Notificación enviada a Socio 2")
            
            # Verificar estado de Socio 2 (debe estar notificado)
            entrada_s2 = lista_espera_service.lista_espera_repo.obtener_por_socio_clase(socio2.id, clase_limite.id)
            log_test("Estado Notificado", entrada_s2.notificado == True, "Socio 2 marcado como notificado")
            
            # Paso B: Socio 2 confirma
            reserva_s2 = lista_espera_service.confirmar_lugar(socio2, clase_limite)
            log_test("Confirmación desde Lista Espera", reserva_s2 is not None, "Reserva creada para Socio 2")
            
        except Exception as e:
            log_test("Flujo Lista de Espera", False, str(e))

        # === TEST 7: VALIDACIÓN SOLICITUD BAJA (Boundary: Texto corto) ===
        try:
            # Intentar crear solicitud con justificación vacía o muy corta
            solicitud_baja_service.crear_solicitud(socio1.id, "Corto")
            log_test("Validación Longitud Justificación", False, "Debería haber fallado por texto corto")
        except ValueError as e:
            log_test("Validación Longitud Justificación", True, f"Correctamente rechazado: {str(e)}")
        except Exception as e:
            log_test("Validación Longitud Justificación", False, f"Error inesperado: {type(e)}")

if __name__ == "__main__":
    run_verification()
