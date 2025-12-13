import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'src', 'instance', 'fitflow.db')

print(f"Checking DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", [t[0] for t in tables])
    
    # Check Socios
    cursor.execute("SELECT id, nombre, apellido, email FROM socios")
    socios = cursor.fetchall()
    print(f"Socios count: {len(socios)}")
    for s in socios:
        print(f"  Socio: {s}")

    # Check Solicitudes
    cursor.execute("SELECT id, socio_id, estado, justificacion FROM solicitudes_baja")
    requests = cursor.fetchall()
    print(f"Solicitudes count: {len(requests)}")
    for r in requests:
        print(f"  Solicitud: {r}")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
