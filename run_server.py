"""Script simple para ejecutar el servidor Flask"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from src.main import create_app
        from src.config.settings import settings
        from waitress import serve
        
        print("Creando aplicación...")
        app = create_app()
        
        print(f"\n{'='*60}")
        print(f"🚀 FitFlow API iniciando en http://{settings.app.host}:{settings.app.port}")
        print(f"   Usando servidor Waitress (producción)")
        print(f"{'='*60}\n")
        
        # Usar waitress en lugar del servidor de desarrollo de Flask
        serve(
            app,
            host=settings.app.host,
            port=settings.app.port,
            threads=4
        )
    except KeyboardInterrupt:
        print("\n\n✋ Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar el servidor: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
