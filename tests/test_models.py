"""Tests para los modelos del dominio"""
import pytest
from datetime import time
from src.models import PlanMembresia, Horario, Entrenador, Clase, Socio
from src.utils.enums import DiaSemana, EstadoMembresia


class TestPlanMembresia:
    """Tests para el modelo PlanMembresia"""
    
    def test_crear_plan(self):
        plan = PlanMembresia(
            titulo="Plan Test",
            descripcion="Plan de prueba",
            precio=10000.0
        )
        assert plan.titulo == "Plan Test"
        assert plan.precio == 10000.0
        assert plan.activo is True


class TestHorario:
    """Tests para el modelo Horario"""
    
    def test_crear_horario_valido(self):
        horario = Horario(
            dia_semana=DiaSemana.LUNES,
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0)
        )
        assert horario.dia_semana == DiaSemana.LUNES
        assert horario.duracion_minutos() == 60
    
    def test_horario_invalido_hora_fin_antes_inicio(self):
        with pytest.raises(ValueError):
            Horario(
                dia_semana=DiaSemana.LUNES,
                hora_inicio=time(10, 0),
                hora_fin=time(9, 0)
            )


class TestClase:
    """Tests para el modelo Clase"""
    
    def test_crear_clase(self):
        entrenador = Entrenador("Test", "Trainer", "test@example.com")
        horario = Horario(DiaSemana.LUNES, time(9, 0), time(10, 0))
        
        clase = Clase(
            titulo="Test Class",
            descripcion="Clase de prueba",
            cupo_maximo=20,
            entrenador=entrenador,
            horario=horario
        )
        
        assert clase.titulo == "Test Class"
        assert clase.cupo_maximo == 20
        assert clase.cupos_disponibles() == 20
    
    def test_cupo_maximo_invalido(self):
        entrenador = Entrenador("Test", "Trainer", "test@example.com")
        horario = Horario(DiaSemana.LUNES, time(9, 0), time(10, 0))
        
        with pytest.raises(ValueError):
            Clase(
                titulo="Test Class",
                descripcion="Clase de prueba",
                cupo_maximo=0,
                entrenador=entrenador,
                horario=horario
            )


class TestSocio:
    """Tests para el modelo Socio"""
    
    def test_crear_socio_sin_plan(self):
        socio = Socio(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com"
        )
        
        assert socio.nombre_completo == "Juan Pérez"
        assert socio.tiene_plan_activo() is False
    
    def test_crear_socio_con_plan(self):
        plan = PlanMembresia("Plan Test", "Descripción", 10000.0)
        socio = Socio(
            nombre="Juan",
            apellido="Pérez",
            dni="12345678",
            email="juan@example.com",
            plan_membresia=plan
        )
        
        assert socio.tiene_plan_activo() is True
        assert socio.estado_membresia == EstadoMembresia.ACTIVA
