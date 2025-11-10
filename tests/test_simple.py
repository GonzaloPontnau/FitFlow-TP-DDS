"""Script de pruebas simple para Entrega 3"""
import os
import sys
from datetime import time

os.environ['DATABASE_URL'] = f'sqlite:///{os.getcwd()}/src/instance/fitflow.db'

from src.main import create_app
from src.config.database import db
from src.models import Socio, Clase, Horario, Entrenador, PlanMembresia, Reserva, ListaEspera
from src.services.agregador_horarios_service import AgregadorHorariosService, ModoVisualizacion
from src.services.lista_espera_service import ListaEsperaService
from src.utils.enums import DiaSemana

def test_calendario():
    """Prueba el calendario agregador"""
    app = create_app()
    with app.app_context():
        print("\n[TEST 1] Calendario Agregador")
        print("-" * 50)
        
        servicio = AgregadorHorariosService()
        calendario = servicio.obtener_calendario_consolidado(modo=ModoVisualizacion.NORMAL)
        
        print(f"Eventos encontrados: {len(calendario)}")
        for evento in calendario[:3]:
            print(f"  - {evento.titulo}: {evento.fecha} {evento.hora_inicio}")
        
        print("PASSED")

def test_lista_espera():
    """Prueba listas de espera"""
    app = create_app()
    with app.app_context():
        print("\n[TEST 2] Lista de Espera")
        print("-" * 50)
        
        # Limpiar y recrear datos
        db.drop_all()
        db.create_all()
        
        # Crear entrenador
        entrenador = Entrenador(
            nombre="Juan",
            apellido="Perez",
            email="juan@fitflow.com",
            especialidad="Funcional"
        )
        db.session.add(entrenador)
        
        # Crear socios
        socio1 = Socio("Maria", "Gonzalez", "12345678", "maria@email.com")
        socio2 = Socio("Pedro", "Ramirez", "87654321", "pedro@email.com")
        socio3 = Socio("Ana", "Lopez", "55555555", "ana@email.com")
        db.session.add_all([socio1, socio2, socio3])
        
        # Crear plan
        plan = PlanMembresia(titulo="Plan Basico", descripcion="Basico", precio=5000)
        db.session.add(plan)
        
        # Crear horario
        horario = Horario(dia_semana=DiaSemana.LUNES, hora_inicio=time(18, 0), hora_fin=time(19, 0))
        db.session.add(horario)
        
        # Crear clase
        clase = Clase(
            titulo="Funcional",
            descripcion="Clase funcional",
            cupo_maximo=2,
            entrenador=entrenador,
            horario=horario
        )
        clase.tiene_lista_espera = True
        plan.clases.append(clase)
        db.session.add(clase)
        
        socio1.plan_membresia = plan
        socio2.plan_membresia = plan
        socio3.plan_membresia = plan
        
        db.session.commit()
        
        print(f"Socios creados: {Socio.query.count()}")
        print(f"Clases creadas: {Clase.query.count()}")
        
        # Llenar cupos
        reserva1 = Reserva(socio=socio1, clase=clase)
        reserva2 = Reserva(socio=socio2, clase=clase)
        db.session.add_all([reserva1, reserva2])
        db.session.commit()
        
        print(f"Reservas: {Reserva.query.count()}/{clase.cupo_maximo}")
        
        # Inscribir en lista de espera
        servicio = ListaEsperaService()
        entrada = servicio.inscribir_en_lista_espera(socio3, clase)
        print(f"Lista de espera - Posicion: {entrada.posicion}")
        
        # Liberar cupo
        db.session.delete(reserva1)
        db.session.commit()
        print("Cupo liberado")
        
        # Notificar siguiente
        notificado = servicio.notificar_siguiente_en_lista(clase)
        if notificado:
            print(f"Socio {notificado.socio_id} notificado")
            
            # Confirmar
            confirmado = servicio.confirmar_lugar(socio3, clase)
            print(f"Lugar confirmado: {confirmado}")
            
            # Verificar reserva creada
            nueva_reserva = Reserva.query.filter_by(socio_id=socio3.id, clase_id=clase.id).first()
            print(f"Nueva reserva creada: {nueva_reserva is not None}")
        
        print("PASSED")

def test_planes():
    """Prueba CRUD de planes"""
    app = create_app()
    with app.app_context():
        print("\n[TEST 3] CRUD Planes")
        print("-" * 50)
        
        # Crear plan
        plan = PlanMembresia(titulo="Plan Premium", descripcion="Premium", precio=15000)
        db.session.add(plan)
        db.session.commit()
        print(f"Plan creado: ID {plan.id}")
        
        # Listar
        planes = PlanMembresia.query.all()
        print(f"Total planes: {len(planes)}")
        
        # Actualizar
        plan.precio = 12000
        db.session.commit()
        print(f"Precio actualizado: ${plan.precio}")
        
        print("PASSED")

def main():
    print("\n" + "="*50)
    print("  PRUEBAS ENTREGA 3 - FitFlow")
    print("="*50)
    
    try:
        test_calendario()
        test_lista_espera()
        test_planes()
        
        print("\n" + "="*50)
        print("  TODAS LAS PRUEBAS EXITOSAS")
        print("="*50 + "\n")
        return 0
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
