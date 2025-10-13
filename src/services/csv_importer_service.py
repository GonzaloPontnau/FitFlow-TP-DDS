"""Servicio de importación de socios desde CSV"""
import pandas as pd
from typing import List, Dict
from src.repositories.socio_repository import SocioRepository
from src.repositories.plan_repository import PlanRepository
from src.models.socio import Socio


class CSVImporterService:
    """
    Servicio para importar socios desde archivos CSV.
    
    Formato esperado del CSV:
    Nombre, Apellido, DNI, Email, ID Plan Membresía
    """
    
    def __init__(self):
        self.socio_repo = SocioRepository()
        self.plan_repo = PlanRepository()
    
    def importar_socios(self, ruta_archivo: str) -> Dict[str, any]:
        """
        Importa socios desde un archivo CSV.
        
        Si un socio con el mismo DNI ya existe, se actualizan sus datos.
        
        Args:
            ruta_archivo: Ruta al archivo CSV
            
        Returns:
            Diccionario con estadísticas de la importación:
            - total: Total de registros procesados
            - creados: Cantidad de socios nuevos creados
            - actualizados: Cantidad de socios actualizados
            - errores: Lista de errores encontrados
        """
        estadisticas = {
            'total': 0,
            'creados': 0,
            'actualizados': 0,
            'errores': []
        }
        
        try:
            # Leer el archivo CSV
            df = pd.read_csv(ruta_archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['Nombre', 'Apellido', 'DNI', 'Email', 'ID Plan Membresía']
            if not all(col in df.columns for col in columnas_requeridas):
                raise ValueError(f"El CSV debe contener las columnas: {columnas_requeridas}")
            
            estadisticas['total'] = len(df)
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    self._procesar_fila(row, estadisticas)
                except Exception as e:
                    error_msg = f"Error en fila {index + 2}: {str(e)}"
                    estadisticas['errores'].append(error_msg)
        
        except FileNotFoundError:
            estadisticas['errores'].append(f"Archivo no encontrado: {ruta_archivo}")
        except pd.errors.EmptyDataError:
            estadisticas['errores'].append("El archivo CSV está vacío")
        except Exception as e:
            estadisticas['errores'].append(f"Error al procesar el archivo: {str(e)}")
        
        return estadisticas
    
    def _procesar_fila(self, row: pd.Series, estadisticas: Dict) -> None:
        """
        Procesa una fila del CSV y crea o actualiza el socio.
        
        Args:
            row: Fila del DataFrame
            estadisticas: Diccionario de estadísticas a actualizar
        """
        nombre = str(row['Nombre']).strip()
        apellido = str(row['Apellido']).strip()
        dni = str(row['DNI']).strip()
        email = str(row['Email']).strip()
        plan_id = int(row['ID Plan Membresía'])
        
        # Validar datos
        if not all([nombre, apellido, dni, email]):
            raise ValueError("Todos los campos son obligatorios")
        
        # Obtener el plan
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan con ID {plan_id} no existe")
        
        # Buscar si el socio ya existe
        socio_existente = self.socio_repo.find_by_dni(dni)
        
        if socio_existente:
            # Actualizar socio existente
            socio_existente.nombre = nombre
            socio_existente.apellido = apellido
            socio_existente.email = email
            socio_existente.asignar_plan(plan)
            self.socio_repo.update(socio_existente)
            estadisticas['actualizados'] += 1
        else:
            # Crear nuevo socio
            nuevo_socio = Socio(
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                email=email,
                plan_membresia=plan
            )
            self.socio_repo.create(nuevo_socio)
            estadisticas['creados'] += 1
    
    def exportar_plantilla(self, ruta_destino: str) -> None:
        """
        Genera un archivo CSV de plantilla para la importación.
        
        Args:
            ruta_destino: Ruta donde guardar la plantilla
        """
        plantilla = pd.DataFrame(columns=[
            'Nombre',
            'Apellido',
            'DNI',
            'Email',
            'ID Plan Membresía'
        ])
        
        # Agregar una fila de ejemplo
        plantilla.loc[0] = ['Juan', 'Pérez', '12345678', 'juan.perez@example.com', 1]
        
        plantilla.to_csv(ruta_destino, index=False)
