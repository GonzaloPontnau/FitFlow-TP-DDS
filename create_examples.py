from datetime import time
from src.main import create_app
from src.config.database import db
from src.models import (
    PlanMembresia, Socio, Entrenador,
    Horario, Clase, Reserva
)
from src.utils.enums import DiaSemana

def create_examples():
    """
    Crea ejemplos de clases ocupadas e inactivas.
    """
    print("Creando ejemplos de clases...")
    app = create_app()
    
    with app.app_context():
        # Obtener entidades necesarias (asumimos que existen por init_data.py)
        entrenador = Entrenador.query.first()
        plan = PlanMembresia.query.first()
        
        if not entrenador or not plan:
            print("Error: Se requieren entrenadores y planes existentes. Ejecuta init_data.py primero.")
            return

        # 1. Crear Clase Ocupada
        print("\n1. Creando Clase Ocupada...")
        horario_ocupada = Horario(DiaSemana.LUNES, time(14, 0), time(15, 0))
        clase_ocupada = Clase(
            "Clase Ocupada Ejemplo", 
            "Esta clase tiene cupo lleno (2/2)", 
            2, # Cupo máximo 2
            entrenador, 
            horario_ocupada
        )
        db.session.add(clase_ocupada)
        db.session.flush()
        clase_ocupada.planes = [plan]
        
        # Crear reservas para llenar el cupo
        # Buscamos 2 socios o creamos temporales si no hay suficientes
        socios = Socio.query.limit(2).all()
        if len(socios) < 2:
            print("  Creando socios temporales para llenar cupo...")
            s1 = Socio("Temp1", "User", "999991", "t1@ex.com", plan)
            s2 = Socio("Temp2", "User", "999992", "t2@ex.com", plan)
            db.session.add_all([s1, s2])
            db.session.flush()
            socios = [s1, s2]
            
        reserva1 = Reserva(socios[0], clase_ocupada)
        reserva2 = Reserva(socios[1], clase_ocupada)
        db.session.add_all([reserva1, reserva2])
        print(f"  ✓ Clase '{clase_ocupada.titulo}' creada con cupo 2 y 2 reservas.")

        # 2. Crear Clase Inactiva
        print("\n2. Creando Clase Inactiva...")
        horario_inactiva = Horario(DiaSemana.VIERNES, time(20, 0), time(21, 0))
        clase_inactiva = Clase(
            "Clase Inactiva Ejemplo", 
            "Esta clase no debería aparecer en listados activos", 
            10, 
            entrenador, 
            horario_inactiva
        )
        # La creamos activa primero para que el init funcione, luego desactivamos
        # Ojo: la clase model tiene default=True en activa
        db.session.add(clase_inactiva)
        db.session.flush()
        clase_inactiva.planes = [plan]
        clase_inactiva.desactivar()
        print(f"  ✓ Clase '{clase_inactiva.titulo}' creada y desactivada.")

        db.session.commit()
        print("\nEjemplos creados exitosamente.")

if __name__ == '__main__':
    create_examples()
