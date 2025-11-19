import pytest
import os
from datetime import time
from src.main import create_app
from src.config.database import db
from src.models import Socio, Clase, Horario, Entrenador, PlanMembresia
from src.utils.enums import DiaSemana

@pytest.fixture
def app():
    """Fixture que crea la aplicación Flask configurada para testing"""
    # Configurar base de datos en memoria o archivo temporal para tests
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['TESTING'] = 'true'
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Fixture que retorna un cliente de pruebas"""
    return app.test_client()

@pytest.fixture
def datos(app):
    """Fixture que crea datos de prueba"""
    with app.app_context():
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
            titulo="Funcional Básico",
            descripcion="Clase de entrenamiento funcional",
            cupo_maximo=2,
            entrenador=entrenador,
            horario=horario1
        )
        clase1.tiene_lista_espera = True
        
        clase2 = Clase(
            titulo="CrossFit",
            descripcion="Clase de CrossFit",
            cupo_maximo=15,
            entrenador=entrenador,
            horario=horario2
        )
        clase2.tiene_lista_espera = True
        
        db.session.add_all([clase1, clase2])
        
        # Asociar clases al plan
        plan.clases.append(clase1)
        plan.clases.append(clase2)
        
        # Asignar plan a socios
        socio1.plan = plan
        socio2.plan = plan
        socio3.plan = plan
        
        db.session.commit()
        
        # Retornar IDs para usar en los tests
        return {
            'socio1': socio1.id,
            'socio2': socio2.id,
            'socio3': socio3.id,
            'clase1': clase1.id,
            'clase2': clase2.id,
            'plan': plan.id
        }
