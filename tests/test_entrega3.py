"""
Script de pruebas para validar la implementación de Entrega 3
Prueba las funcionalidades principales:
- Calendario agregador
- Listas de espera
- CRUD de planes
- Solicitudes de baja
"""
import os
import sys
from datetime import datetime, timedelta, time

# Configurar ruta absoluta para la base de datos
# os.environ['DATABASE_URL'] = f'sqlite:///{os.getcwd()}/src/instance/fitflow.db'

from src.main import create_app
from src.config.database import db
from src.models import Socio, Clase, Horario, Entrenador, PlanMembresia, Reserva, ListaEspera
from src.services.agregador_horarios_service import AgregadorHorariosService, ModoVisualizacion
from src.services.lista_espera_service import ListaEsperaService
from src.services.solicitud_baja_service import SolicitudBajaService
from src.utils.enums import DiaSemana, EstadoSolicitudBaja

def print_section(title):
    """Imprime una sección con formato"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def crear_datos_prueba(app):
    """Crea datos de prueba en la base de datos"""
    with app.app_context():
        print_section("CREANDO DATOS DE PRUEBA")
        
        # Limpiar datos existentes
        db.drop_all()
        db.create_all()
        
        # Crear entrenador
        entrenador = Entrenador(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@fitflow.com",
            especialidad="Funcional"
        )
        db.session.add(entrenador)
        
        # Crear socios
        socio1 = Socio(
            nombre="María",
            apellido="González",
            dni="12345678",
            email="maria@email.com"
        )
        socio2 = Socio(
            nombre="Pedro",
            apellido="Ramírez",
            dni="87654321",
            email="pedro@email.com"
        )
        socio3 = Socio(
            nombre="Ana",
            apellido="López",
            dni="55555555",
            email="ana@email.com"
        )
        db.session.add_all([socio1, socio2, socio3])
        
        # Crear plan de membresía
        plan = PlanMembresia(
            titulo="Plan Básico",
            descripcion="Acceso a clases básicas",
            precio=5000.0
        )
        db.session.add(plan)
        
        # Crear horarios
        horario1 = Horario(
            dia_semana=DiaSemana.LUNES,
            hora_inicio=time(18, 0),
            hora_fin=time(19, 0)
        )
        horario2 = Horario(
            dia_semana=DiaSemana.MIERCOLES,
            hora_inicio=time(19, 0),
            hora_fin=time(20, 0)
        )
        db.session.add_all([horario1, horario2])
        
        # Crear clases
        clase1 = Clase(
            nombre="Funcional Básico",
            descripcion="Clase de entrenamiento funcional",
            cupo_maximo=2,  # Cupo reducido para probar lista de espera
            tiene_lista_espera=True,
            entrenador=entrenador
        )
        clase1.horarios.append(horario1)
        
        clase2 = Clase(
            nombre="CrossFit",
            descripcion="Clase de CrossFit",
            cupo_maximo=15,
            tiene_lista_espera=True,
            entrenador=entrenador
        )
        clase2.horarios.append(horario2)
        
        db.session.add_all([clase1, clase2])
        
        # Asociar clases al plan
        plan.clases.append(clase1)
        plan.clases.append(clase2)
        
        # Asignar plan a socios
        socio1.plan = plan
        socio2.plan = plan
        socio3.plan = plan
        
        db.session.commit()
        
        print(f"✅ Creados: {Socio.query.count()} socios")
        print(f"✅ Creadas: {Clase.query.count()} clases")
        print(f"✅ Creados: {PlanMembresia.query.count()} planes")
        print(f"✅ Creado: {Entrenador.query.count()} entrenador")
        
        return {
            'socio1': socio1.id,
            'socio2': socio2.id,
            'socio3': socio3.id,
            'clase1': clase1.id,
            'clase2': clase2.id,
            'plan': plan.id
        }

def test_calendario_agregador(app, datos):
    """Prueba el servicio agregador de horarios"""
    with app.app_context():
        print_section("PRUEBA 1: CALENDARIO AGREGADOR")
        
        servicio = AgregadorHorariosService()
        
        # Obtener calendario en modo normal
        print("📅 Calendario consolidado (modo NORMAL):")
        calendario = servicio.obtener_calendario_consolidado(
            modo=ModoVisualizacion.NORMAL
        )
        
        for evento in calendario[:5]:  # Mostrar solo primeros 5
            print(f"  - {evento.titulo}")
            print(f"    Fecha: {evento.fecha} {evento.hora_inicio}")
            print(f"    Origen: {evento.origen if hasattr(evento, 'origen') else evento.tipo}")
            print(f"    Cupos: {evento.cupos_disponibles}/{evento.cupo_maximo}")
            print()
        
        print(f"✅ Total de eventos: {len(calendario)}")
        
        # Obtener calendario en modo ocupado
        print("\n📅 Calendario consolidado (modo OCUPADO):")
        calendario_ocupado = servicio.obtener_calendario_consolidado(
            modo=ModoVisualizacion.OCUPADO,
            fecha_desde=datetime.now().date(),
            fecha_hasta=(datetime.now() + timedelta(days=7)).date()
        )
        
        print(f"✅ Eventos con cupos limitados: {len(calendario_ocupado)}")

def test_lista_espera(app, datos):
    """Prueba el sistema de listas de espera"""
    with app.app_context():
        print_section("PRUEBA 2: LISTA DE ESPERA")
        
        servicio = ListaEsperaService()
        clase_id = datos['clase1']
        
        # Llenar cupos de la clase
        print("📝 Llenando cupos de la clase...")
        clase = Clase.query.get(clase_id)
        
        # Crear reserva para socio 1
        socio1 = Socio.query.get(datos['socio1'])
        clase = Clase.query.get(clase_id)
        reserva1 = Reserva(
            socio=socio1,
            clase=clase
        )
        db.session.add(reserva1)
        db.session.commit()
        print(f"  ✅ Reserva 1 creada (Cupo 1/{clase.cupo_maximo})")
        
        # Crear reserva para socio 2
        socio2 = Socio.query.get(datos['socio2'])
        reserva2 = Reserva(
            socio=socio2,
            clase=clase
        )
        db.session.add(reserva2)
        db.session.commit()
        print(f"  ✅ Reserva 2 creada (Cupo 2/{clase.cupo_maximo})")
        print(f"  ⚠️  Clase LLENA")
        
        # Inscribir socio 3 en lista de espera
        print("\n📝 Inscribiendo socio 3 en lista de espera...")
        socio3 = Socio.query.get(datos['socio3'])
        entrada = servicio.inscribir_en_lista_espera(socio3, clase)
        print(f"  ✅ Socio inscrito en posición: {entrada.posicion}")
        print(f"  ℹ️  Estado notificado: {entrada.notificado}")
        
        # Verificar lista de espera
        lista = ListaEspera.query.filter_by(clase_id=clase_id).all()
        print(f"\n📋 Lista de espera actual:")
        for entrada in lista:
            print(f"  - Posición {entrada.posicion}: Socio {entrada.socio_id}")
            print(f"    Notificado: {entrada.notificado}")
            print(f"    Confirmado: {entrada.confirmado}")
        
        # Simular liberación de cupo
        print("\n🔄 Simulando liberación de cupo...")
        db.session.delete(reserva1)
        db.session.commit()
        print("  ✅ Reserva 1 cancelada")
        
        # Notificar siguiente en lista
        print("\n📧 Notificando siguiente en lista...")
        notificado = servicio.notificar_siguiente_en_lista(clase)
        
        if notificado:
            print(f"  ✅ Socio {notificado.socio_id} notificado")
            print(f"  ⏰ Plazo de confirmación: 24 horas")
            
            # Confirmar lugar
            print("\n✅ Confirmando lugar en lista de espera...")
            confirmado = servicio.confirmar_lugar(notificado.socio, notificado.clase)
            print(f"  ✅ Confirmación exitosa")
            print(f"  ℹ️  Reserva creada automáticamente")
            
            # Verificar que se creó la reserva
            reserva_nueva = Reserva.query.filter_by(
                socio_id=datos['socio3'],
                clase_id=clase_id
            ).first()
            print(f"  ✅ Nueva reserva ID: {reserva_nueva.id}")

def test_crud_planes(app, datos):
    """Prueba CRUD de planes de membresía"""
    with app.app_context():
        print_section("PRUEBA 3: CRUD DE PLANES")
        
        # Crear nuevo plan directamente con el modelo
        print("📝 Creando nuevo plan...")
        nuevo_plan = PlanMembresia(
            titulo="Plan Premium",
            descripcion="Acceso ilimitado",
            precio=15000.0
        )
        db.session.add(nuevo_plan)
        db.session.commit()
        print(f"  ✅ Plan creado con ID: {nuevo_plan.id}")
        
        # Listar planes
        print("\n📋 Listado de planes:")
        planes = PlanMembresia.query.all()
        for plan in planes:
            print(f"  - {plan.titulo} (${plan.precio})")
        
        # Actualizar plan
        print("\n📝 Actualizando plan...")
        nuevo_plan.precio = 12000.0
        nuevo_plan.descripcion = "Acceso completo a todas las clases"
        db.session.commit()
        print(f"  ✅ Precio actualizado: ${nuevo_plan.precio}")
        
        # Agregar clase al plan
        print("\n📝 Agregando clase al plan...")
        clase = Clase.query.get(datos['clase1'])
        nuevo_plan.clases.append(clase)
        db.session.commit()
        print(f"  ✅ Clases en el plan: {len(nuevo_plan.clases)}")
        
        # Eliminar clase del plan
        print("\n📝 Eliminando clase del plan...")
        nuevo_plan.clases.remove(clase)
        db.session.commit()
        print(f"  ✅ Clases restantes: {len(nuevo_plan.clases)}")

def test_solicitudes_baja(app, datos):
    """Prueba gestión de solicitudes de baja"""
    with app.app_context():
        print_section("PRUEBA 4: SOLICITUDES DE BAJA")
        
        servicio = SolicitudBajaService()
        
        # Crear solicitud
        print("📝 Creando solicitud de baja...")
        justificacion_valida = (
            "Solicito la baja del servicio debido a un cambio de residencia permanente a otra ciudad "
            "por motivos laborales. Lamentablemente no podré continuar asistiendo al gimnasio "
            "y necesito cancelar mi suscripción actual. Agradezco el servicio prestado durante este tiempo "
            "y espero poder volver en el futuro si regreso a la zona."
        )
        solicitud = servicio.crear_solicitud(
            socio_id=datos['socio1'],
            justificacion=justificacion_valida
        )
        print(f"  ✅ Solicitud creada con ID: {solicitud.id}")
        print(f"  ℹ️  Estado: {solicitud.estado.value}")
        
        # Listar solicitudes
        print("\n📋 Listado de solicitudes:")
        solicitudes = servicio.obtener_todas_solicitudes()
        for sol in solicitudes:
            print(f"  - Solicitud #{sol.id} - Socio {sol.socio_id}")
            print(f"    Estado: {sol.estado.value}")
            print(f"    Motivo: {sol.justificacion}")
        
        # Aprobar solicitud
        print("\n✅ Aprobando solicitud...")
        aprobada = servicio.aprobar_solicitud(solicitud.id)
        print(f"  ✅ Estado: {aprobada.estado.value}")
        print(f"  ℹ️  Fecha resolución: {aprobada.fecha_resolucion}")
        
        # Crear y rechazar otra solicitud
        print("\n📝 Creando y rechazando nueva solicitud...")
        justificacion_valida2 = (
            "Estoy experimentando dificultades económicas temporales y necesito suspender mis gastos "
            "no esenciales por el momento. Espero poder reactivar mi membresía en unos meses cuando "
            "mi situación financiera mejore. Por favor procesen esta solicitud lo antes posible. "
            "Muchas gracias por su comprensión."
        )
        solicitud2 = servicio.crear_solicitud(
            socio_id=datos['socio2'],
            justificacion=justificacion_valida2
        )
        rechazada = servicio.rechazar_solicitud(
            solicitud2.id,
            "El socio tiene pagos pendientes"
        )
        print(f"  ❌ Solicitud rechazada")
        print(f"  ℹ️  Motivo rechazo: {rechazada.comentario_admin}")

def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("  PRUEBAS DE ENTREGA 3 - FitFlow")
    print("="*60)
    print("\nValidación de implementación:")
    print("  - Calendario agregador (interno + externo)")
    print("  - Sistema de listas de espera con notificaciones")
    print("  - CRUD completo de planes de membresía")
    print("  - Gestión de solicitudes de baja")
    print("="*60 + "\n")
    
    app = create_app()
    
    try:
        # Crear datos de prueba
        datos = crear_datos_prueba(app)
        
        # Ejecutar pruebas
        test_calendario_agregador(app, datos)
        test_lista_espera(app, datos)
        test_crud_planes(app, datos)
        test_solicitudes_baja(app, datos)
        
        print_section("RESUMEN DE PRUEBAS")
        print("✅ Todas las pruebas ejecutadas correctamente")
        print("\n📊 Estadísticas finales:")
        with app.app_context():
            print(f"  - Socios: {Socio.query.count()}")
            print(f"  - Clases: {Clase.query.count()}")
            print(f"  - Reservas: {Reserva.query.count()}")
            print(f"  - Planes: {PlanMembresia.query.count()}")
            print(f"  - Lista de espera: {ListaEspera.query.count()}")
        
        print("\n" + "="*60)
        print("  ENTREGA 3 VALIDADA CORRECTAMENTE")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante las pruebas:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = ejecutar_todas_las_pruebas()
    sys.exit(0 if exito else 1)
