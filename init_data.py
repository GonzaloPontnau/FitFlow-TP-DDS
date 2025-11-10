"""Script para inicializar la base de datos con datos de ejemplo"""
from datetime import time
from src.main import create_app
from src.config.database import db
from src.models import (
    PlanMembresia, Socio, Entrenador,
    Horario, Clase, Reserva
)
from src.utils.enums import DiaSemana

def init_database():
    """
    Inicializa la base de datos con datos de ejemplo.
    
    Crea las tablas y carga datos iniciales para desarrollo/testing.
    """
    print("Inicializando base de datos con datos de ejemplo...")
    app = create_app()
    
    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✓ Tablas de base de datos creadas")
        
        # Limpiar datos existentes (opcional)
        print("Limpiando datos existentes...")
        Reserva.query.delete()
        Clase.query.delete()
        Horario.query.delete()
        Entrenador.query.delete()
        Socio.query.delete()
        PlanMembresia.query.delete()
        db.session.commit()
        print("✓ Datos existentes eliminados")
        
        # Crear planes de membresía
        print("\nCreando planes de membresía...")
        plan_basico = PlanMembresia(
            "Plan Básico",
            "Acceso a gimnasio de lunes a viernes de 6:00 a 16:00 y clases grupales básicas",
            15000.0
        )
        plan_premium = PlanMembresia(
            "Plan Premium",
            "Acceso completo al gimnasio, todas las clases grupales, nutricionista y entrenador personal",
            25000.0
        )
        plan_estudiante = PlanMembresia(
            "Plan Estudiante",
            "Plan especial para estudiantes con descuento. Acceso al gimnasio y clases básicas",
            12000.0
        )
        
        db.session.add_all([plan_basico, plan_premium, plan_estudiante])
        db.session.commit()
        print(f"✓ {PlanMembresia.query.count()} planes creados")
        
        # Crear entrenadores
        print("\nCreando entrenadores...")
        entrenador1 = Entrenador("Carlos", "Rodríguez", "Instructor de Spinning certificado con 5 años de experiencia")
        entrenador2 = Entrenador("María", "García", "Profesora de Yoga y Pilates")
        entrenador3 = Entrenador("Juan", "Martínez", "Entrenador Personal y CrossFit")
        entrenador4 = Entrenador("Ana", "López", "Instructora de Zumba y Baile")
        entrenador5 = Entrenador("Pedro", "Sánchez", "Profesor de Funcional y TRX")
        
        db.session.add_all([entrenador1, entrenador2, entrenador3, entrenador4, entrenador5])
        db.session.commit()
        print(f"✓ {Entrenador.query.count()} entrenadores creados")
        
        # Crear horarios y clases
        print("\nCreando clases y horarios...")
        
        # Spinning - Lunes 18:00
        horario1 = Horario(DiaSemana.LUNES, time(18, 0), time(19, 0))
        clase1 = Clase("Spinning Intenso", "Clase de spinning de alta intensidad para quemar calorías", 20, entrenador1, horario1)
        db.session.add(clase1)
        db.session.flush()
        clase1.planes = [plan_premium, plan_basico]
        
        # Yoga - Miércoles 10:00
        horario2 = Horario(DiaSemana.MIERCOLES, time(10, 0), time(10, 45))
        clase2 = Clase("Yoga Matutino", "Sesión de yoga relajante para comenzar el día", 15, entrenador2, horario2)
        db.session.add(clase2)
        db.session.flush()
        clase2.planes = [plan_basico, plan_premium, plan_estudiante]
        
        # CrossFit - Martes 19:00
        horario3 = Horario(DiaSemana.MARTES, time(19, 0), time(20, 0))
        clase3 = Clase("CrossFit Avanzado", "Entrenamiento funcional de alta intensidad", 12, entrenador3, horario3)
        db.session.add(clase3)
        db.session.flush()
        clase3.planes = [plan_premium]
        
        # Zumba - Jueves 18:30
        horario4 = Horario(DiaSemana.JUEVES, time(18, 30), time(19, 30))
        clase4 = Clase("Zumba Fitness", "Baile y ejercicio cardiovascular al ritmo de música latina", 25, entrenador4, horario4)
        db.session.add(clase4)
        db.session.flush()
        clase4.planes = [plan_basico, plan_premium, plan_estudiante]
        
        # Funcional - Viernes 17:00
        horario5 = Horario(DiaSemana.VIERNES, time(17, 0), time(18, 0))
        clase5 = Clase("Funcional TRX", "Entrenamiento funcional con bandas de suspensión", 15, entrenador5, horario5)
        db.session.add(clase5)
        db.session.flush()
        clase5.planes = [plan_premium, plan_basico]
        
        # Pilates - Lunes 9:00
        horario6 = Horario(DiaSemana.LUNES, time(9, 0), time(10, 0))
        clase6 = Clase("Pilates", "Fortalecimiento del core y mejora de la postura", 18, entrenador2, horario6)
        db.session.add(clase6)
        db.session.flush()
        clase6.planes = [plan_basico, plan_premium, plan_estudiante]
        
        # Spinning - Sábado 11:00
        horario7 = Horario(DiaSemana.SABADO, time(11, 0), time(12, 0))
        clase7 = Clase("Spinning Weekend", "Clase de spinning para el fin de semana", 20, entrenador1, horario7)
        db.session.add(clase7)
        db.session.flush()
        clase7.planes = [plan_premium, plan_basico]
        
        db.session.commit()
        print(f"✓ {Clase.query.count()} clases creadas")
        
        # Crear socios
        print("\nCreando socios...")
        socio1 = Socio("Juan", "Pérez", "12345678", "juan.perez@example.com", plan_premium)
        socio2 = Socio("María", "González", "23456789", "maria.gonzalez@example.com", plan_basico)
        socio3 = Socio("Carlos", "Fernández", "34567890", "carlos.fernandez@example.com", plan_premium)
        socio4 = Socio("Ana", "Martínez", "45678901", "ana.martinez@example.com", plan_estudiante)
        socio5 = Socio("Luis", "Rodríguez", "56789012", "luis.rodriguez@example.com", plan_basico)
        socio6 = Socio("Laura", "López", "67890123", "laura.lopez@example.com", plan_premium)
        socio7 = Socio("Diego", "Sánchez", "78901234", "diego.sanchez@example.com", plan_estudiante)
        socio8 = Socio("Sofía", "Ramírez", "89012345", "sofia.ramirez@example.com", plan_basico)
        
        db.session.add_all([socio1, socio2, socio3, socio4, socio5, socio6, socio7, socio8])
        db.session.commit()
        print(f"✓ {Socio.query.count()} socios creados")
        
        # Crear algunas reservas
        print("\nCreando reservas...")
        reserva1 = Reserva(socio1, clase1)  # Juan en Spinning Intenso
        reserva2 = Reserva(socio2, clase2)  # María en Yoga
        reserva3 = Reserva(socio3, clase3)  # Carlos en CrossFit
        reserva4 = Reserva(socio4, clase4)  # Ana en Zumba
        reserva5 = Reserva(socio1, clase2)  # Juan en Yoga
        reserva6 = Reserva(socio6, clase1)  # Laura en Spinning
        reserva7 = Reserva(socio6, clase3)  # Laura en CrossFit
        reserva8 = Reserva(socio5, clase4)  # Luis en Zumba
        reserva9 = Reserva(socio7, clase2)  # Diego en Yoga
        reserva10 = Reserva(socio8, clase6) # Sofía en Pilates
        
        db.session.add_all([reserva1, reserva2, reserva3, reserva4, reserva5, 
                           reserva6, reserva7, reserva8, reserva9, reserva10])
        db.session.commit()
        print(f"✓ {Reserva.query.count()} reservas creadas")
        
        print("\n" + "="*60)
        print("✓ Base de datos inicializada correctamente con datos de ejemplo")
        print("="*60)
        print("\nResumen:")
        print(f"  - Planes de membresía: {PlanMembresia.query.count()}")
        print(f"  - Entrenadores: {Entrenador.query.count()}")
        print(f"  - Clases: {Clase.query.count()}")
        print(f"  - Socios: {Socio.query.count()}")
        print(f"  - Reservas: {Reserva.query.count()}")
        print("\n¡Puedes comenzar a probar la aplicación!")


if __name__ == '__main__':
    init_database()
