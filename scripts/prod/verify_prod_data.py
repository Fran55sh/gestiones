#!/usr/bin/env python3
"""
Script para verificar que los datos en producción están correctos.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.carteras.models import Cartera
from app.features.cases.models import Case, CaseStatus
from app.features.users.models import User
from app.features.activities.models import Activity
from app.features.cases.promise import Promise

def verify_data():
    """Verifica que los datos en producción están correctos."""
    app = create_app()
    
    with app.app_context():
        print("[VERIFY] Verificando datos en producción...\n")
        
        # Verificar carteras
        carteras = Cartera.query.all()
        print(f"[CARTERAS] {len(carteras)}")
        for cartera in carteras:
            print(f"   - {cartera.nombre} (ID: {cartera.id}, Activo: {cartera.activo})")
        
        # Verificar estados
        statuses = CaseStatus.query.all()
        print(f"\n[STATUSES] {len(statuses)}")
        for status in statuses:
            print(f"   - {status.nombre} (ID: {status.id}, Activo: {status.activo})")
        
        # Verificar casos
        cases = Case.query.all()
        print(f"\n[CASES] {len(cases)}")
        if cases:
            print(f"   - Primer caso: {cases[0].name} {cases[0].lastname} (nro_cliente: {cases[0].nro_cliente})")
        
        # Verificar usuarios
        users = User.query.all()
        print(f"\n[USERS] {len(users)}")
        for user in users:
            print(f"   - {user.username} (Rol: {user.role}, Activo: {user.active})")
        
        # Verificar actividades
        activities = Activity.query.all()
        print(f"\n[ACTIVITIES] {len(activities)}")
        
        # Verificar promesas
        promises = Promise.query.all()
        print(f"\n[PROMISES] {len(promises)}")
        
        # Verificar relaciones
        print(f"\n[RELATIONS] Verificando relaciones...")
        casos_sin_cartera = Case.query.filter(Case.cartera_id.is_(None)).count()
        casos_sin_status = Case.query.filter(Case.status_id.is_(None)).count()
        actividades_sin_caso = Activity.query.filter(Activity.case_id.is_(None)).count()
        promesas_sin_caso = Promise.query.filter(Promise.case_id.is_(None)).count()
        
        if casos_sin_cartera > 0:
            print(f"   [WARN] {casos_sin_cartera} casos sin cartera asignada")
        if casos_sin_status > 0:
            print(f"   [WARN] {casos_sin_status} casos sin estado asignado")
        if actividades_sin_caso > 0:
            print(f"   [WARN] {actividades_sin_caso} actividades sin caso asignado")
        if promesas_sin_caso > 0:
            print(f"   [WARN] {promesas_sin_caso} promesas sin caso asignado")
        
        if casos_sin_cartera == 0 and casos_sin_status == 0 and actividades_sin_caso == 0 and promesas_sin_caso == 0:
            print("   [OK] Todas las relaciones están correctas")
        
        print(f"\n[SUCCESS] Verificación completada!")
        print(f"\n[SUMMARY] Resumen:")
        print(f"   - Carteras: {len(carteras)}")
        print(f"   - Estados: {len(statuses)}")
        print(f"   - Casos: {len(cases)}")
        print(f"   - Usuarios: {len(users)}")
        print(f"   - Actividades: {len(activities)}")
        print(f"   - Promesas: {len(promises)}")

if __name__ == '__main__':
    verify_data()

