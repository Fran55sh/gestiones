#!/usr/bin/env python3
"""
Script para asignar casos a un gestor.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.cases.models import Case

def assign_cases():
    """Asigna casos a un gestor."""
    app = create_app()
    
    with app.app_context():
        # Casos a asignar: ID -> assigned_to_id
        casos_a_asignar = {
            7: 2,  # Caso ID 7 -> gestor ID 2
            8: 2,  # Caso ID 8 -> gestor ID 2
        }
        
        actualizados = 0
        errores = 0
        
        for case_id, gestor_id in casos_a_asignar.items():
            try:
                caso = Case.query.get(case_id)
                
                if not caso:
                    print(f"[ERROR] No se encontró caso con ID: {case_id}")
                    errores += 1
                    continue
                
                print(f"[INFO] Caso ID {case_id} (nro_cliente: {caso.nro_cliente}):")
                print(f"       assigned_to_id actual: {caso.assigned_to_id}")
                print(f"       assigned_to_id nuevo:  {gestor_id}")
                
                caso.assigned_to_id = gestor_id
                actualizados += 1
                
            except Exception as e:
                print(f"[ERROR] Error actualizando caso {case_id}: {e}")
                errores += 1
                continue
        
        # Guardar cambios
        if actualizados > 0:
            try:
                db.session.commit()
                print(f"\n[OK] {actualizados} casos actualizados correctamente")
            except Exception as e:
                db.session.rollback()
                print(f"\n[ERROR] Error al guardar cambios: {e}")
                errores += actualizados
                actualizados = 0
        
        if errores > 0:
            print(f"[WARN] {errores} errores encontrados")
        
        print(f"\n[RESUMEN] Actualizados: {actualizados}, Errores: {errores}")

if __name__ == '__main__':
    assign_cases()

