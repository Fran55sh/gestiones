"""
Script para actualizar los casos existentes con management_status por defecto.
"""
import sys
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.db import db
from app.models import Case

def update_existing_cases():
    """Actualiza los casos existentes con management_status por defecto."""
    app = create_app()
    
    with app.app_context():
        # Obtener todos los casos
        all_cases = Case.query.all()
        print(f"Total de casos en la BD: {len(all_cases)}")
        
        # Obtener casos sin management_status o con management_status vacío
        cases_to_update = []
        for case in all_cases:
            if not case.management_status or case.management_status == '':
                cases_to_update.append(case)
        
        if not cases_to_update:
            print("No hay casos para actualizar (todos ya tienen management_status).")
            return
        
        print(f"Actualizando {len(cases_to_update)} casos...")
        
        # Mapeo de status a management_status
        status_to_management = {
            'en_gestion': 'contactado',
            'promesa': 'con-arreglo',
            'pagada': 'pagada',
            'incobrable': 'incobrable'
        }
        
        updated = 0
        for case in cases_to_update:
            # Mapear el status existente a management_status
            old_mgmt_status = case.management_status
            case.management_status = status_to_management.get(case.status, 'sin-gestion')
            print(f"  Caso {case.id}: status={case.status}, management_status={old_mgmt_status} -> {case.management_status}")
            updated += 1
        
        db.session.commit()
        print(f"OK: {updated} casos actualizados exitosamente.")

if __name__ == '__main__':
    update_existing_cases()

