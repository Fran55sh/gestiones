#!/usr/bin/env python3
"""
Script para exportar datos de develop para importar en producción.
Exporta: carteras, case_statuses, casos, usuarios, actividades, promesas.
"""
import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.carteras.models import Cartera
from app.features.cases.models import Case, CaseStatus
from app.features.users.models import User
from app.features.activities.models import Activity
from app.features.cases.promise import Promise

def export_data():
    """Exporta todos los datos necesarios para producción."""
    app = create_app()
    
    with app.app_context():
        export_data = {
            'exported_at': datetime.now(timezone.utc).isoformat(),
            'carteras': [],
            'case_statuses': [],
            'cases': [],
            'users': [],
            'activities': [],
            'promises': []
        }
        
        # Exportar carteras
        print("[EXPORT] Exportando carteras...")
        carteras = Cartera.query.all()
        for cartera in carteras:
            export_data['carteras'].append({
                'id': cartera.id,
                'nombre': cartera.nombre,
                'activo': cartera.activo,
                'created_at': cartera.created_at.isoformat() if cartera.created_at else None
            })
        print(f"   [OK] {len(export_data['carteras'])} carteras exportadas")
        
        # Exportar case_statuses
        print("[EXPORT] Exportando estados de caso...")
        statuses = CaseStatus.query.all()
        for status in statuses:
            export_data['case_statuses'].append({
                'id': status.id,
                'nombre': status.nombre,
                'activo': status.activo,
                'created_at': status.created_at.isoformat() if status.created_at else None
            })
        print(f"   [OK] {len(export_data['case_statuses'])} estados exportados")
        
        # Exportar casos
        print("[EXPORT] Exportando casos...")
        cases = Case.query.all()
        for case in cases:
            export_data['cases'].append({
                'id': case.id,  # Incluir ID original para mapeo de actividades/promesas
                'nro_cliente': case.nro_cliente,
                'name': case.name,
                'lastname': case.lastname,
                'dni': case.dni,
                'total': float(case.total) if case.total else 0.0,
                'monto_inicial': float(case.monto_inicial) if case.monto_inicial else None,
                'fecha_ultimo_pago': case.fecha_ultimo_pago.isoformat() if case.fecha_ultimo_pago else None,
                'telefono': case.telefono,
                'calle_nombre': case.calle_nombre,
                'calle_nro': case.calle_nro,
                'localidad': case.localidad,
                'cp': case.cp,
                'provincia': case.provincia,
                'status_id': case.status_id,
                'cartera_id': case.cartera_id,
                'assigned_to_id': case.assigned_to_id,
                'notes': case.notes,
                'created_at': case.created_at.isoformat() if case.created_at else None,
                'updated_at': case.updated_at.isoformat() if case.updated_at else None
            })
        print(f"   [OK] {len(export_data['cases'])} casos exportados")
        
        # Exportar usuarios (solo los que no son admin por defecto)
        print("[EXPORT] Exportando usuarios...")
        users = User.query.all()
        for user in users:
            # No exportar contraseñas, solo estructura
            export_data['users'].append({
                'username': user.username,
                'role': user.role,
                'active': user.active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        print(f"   [OK] {len(export_data['users'])} usuarios exportados")
        
        # Exportar actividades
        print("[EXPORT] Exportando actividades...")
        activities = Activity.query.all()
        for activity in activities:
            export_data['activities'].append({
                'case_id': activity.case_id,
                'type': activity.type,
                'notes': activity.notes,
                'created_by_id': activity.created_by_id,
                'created_at': activity.created_at.isoformat() if activity.created_at else None
            })
        print(f"   [OK] {len(export_data['activities'])} actividades exportadas")
        
        # Exportar promesas
        print("[EXPORT] Exportando promesas...")
        promises = Promise.query.all()
        for promise in promises:
            export_data['promises'].append({
                'case_id': promise.case_id,
                'amount': float(promise.amount) if promise.amount else 0.0,
                'promise_date': promise.promise_date.isoformat() if promise.promise_date else None,
                'status': promise.status,
                'fulfilled_date': promise.fulfilled_date.isoformat() if promise.fulfilled_date else None,
                'notes': promise.notes,
                'created_at': promise.created_at.isoformat() if promise.created_at else None,
                'updated_at': promise.updated_at.isoformat() if promise.updated_at else None
            })
        print(f"   [OK] {len(export_data['promises'])} promesas exportadas")
        
        # Guardar en archivo JSON
        output_file = 'data/export_for_prod.json'
        os.makedirs('data', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n[SUCCESS] Datos exportados a: {output_file}")
        print(f"\n[SUMMARY] Resumen:")
        print(f"   - Carteras: {len(export_data['carteras'])}")
        print(f"   - Estados: {len(export_data['case_statuses'])}")
        print(f"   - Casos: {len(export_data['cases'])}")
        print(f"   - Usuarios: {len(export_data['users'])}")
        print(f"   - Actividades: {len(export_data['activities'])}")
        print(f"   - Promesas: {len(export_data['promises'])}")

if __name__ == '__main__':
    export_data()

