#!/usr/bin/env python3
"""
Script para crear datos de muestra para pruebas.
"""
import sys
from datetime import datetime, date, timedelta
from decimal import Decimal

# Agregar el directorio raíz al path
sys.path.insert(0, '.')

from app import create_app
from app.core.database import db
from app.features.users.models import User
from app.features.cases.models import Case
from app.features.cases.promise import Promise
from app.features.activities.models import Activity


def create_sample_data():
    """Crea datos de muestra para pruebas."""
    app = create_app()
    
    with app.app_context():
        print("📦 Creando datos de muestra...")
        
        # Obtener o crear usuarios
        admin = User.query.filter_by(username='admin').first()
        gestor = User.query.filter_by(username='gestor').first()
        
        if not admin:
            admin = User(username='admin', role='admin', active=True)
            admin.set_password('admin123')
            db.session.add(admin)
            print("  ✅ Usuario admin creado")
        
        if not gestor:
            gestor = User(username='gestor', role='gestor', active=True)
            gestor.set_password('gestor123')
            db.session.add(gestor)
            print("  ✅ Usuario gestor creado")
        
        db.session.commit()
        
        # Crear casos de ejemplo
        cases_data = [
            {
                'entity': 'Banco Nacional',
                'debtor_name': 'Carlos Rodríguez',
                'dni': '12345678',
                'amount': Decimal('50000.00'),
                'status': 'pagada',
                'cartera': 'Cartera A',
                'assigned_to': gestor
            },
            {
                'entity': 'Cooperativa El Ahorro',
                'debtor_name': 'María González',
                'dni': '23456789',
                'amount': Decimal('75000.00'),
                'status': 'en_gestion',
                'cartera': 'Cartera A',
                'assigned_to': gestor
            },
            {
                'entity': 'Financiera Express',
                'debtor_name': 'Pedro Martínez',
                'dni': '34567890',
                'amount': Decimal('30000.00'),
                'status': 'promesa',
                'cartera': 'Cartera B',
                'assigned_to': gestor
            },
            {
                'entity': 'Banco Comercial',
                'debtor_name': 'Ana López',
                'dni': '45678901',
                'amount': Decimal('100000.00'),
                'status': 'en_gestion',
                'cartera': 'Cartera B',
                'assigned_to': gestor
            },
            {
                'entity': 'Cooperativa Popular',
                'debtor_name': 'Luis Fernández',
                'dni': '56789012',
                'amount': Decimal('25000.00'),
                'status': 'pagada',
                'cartera': 'Cartera C',
                'assigned_to': gestor
            },
        ]
        
        cases_created = []
        for case_data in cases_data:
            # Verificar si el caso ya existe
            existing = Case.query.filter_by(
                entity=case_data['entity'],
                debtor_name=case_data['debtor_name']
            ).first()
            
            if existing:
                print(f"  ⏭️  Caso ya existe: {case_data['entity']} - {case_data['debtor_name']}")
                cases_created.append(existing)
                continue
            
            case = Case(
                entity=case_data['entity'],
                debtor_name=case_data['debtor_name'],
                dni=case_data['dni'],
                amount=case_data['amount'],
                status=case_data['status'],
                cartera=case_data['cartera'],
                assigned_to_id=case_data['assigned_to'].id if case_data['assigned_to'] else None
            )
            db.session.add(case)
            cases_created.append(case)
            print(f"  ✅ Caso creado: {case_data['entity']} - ${case_data['amount']}")
        
        db.session.commit()
        
        # Crear promesas para algunos casos
        print("\n📅 Creando promesas...")
        for case in cases_created[:3]:  # Primeros 3 casos
            if case.status == 'promesa' or case.status == 'en_gestion':
                # Verificar si ya tiene promesas
                if case.promises.count() > 0:
                    print(f"  ⏭️  Caso {case.id} ya tiene promesas")
                    continue
                
                promise = Promise(
                    case_id=case.id,
                    amount=case.amount * Decimal('0.5'),  # 50% del monto
                    promise_date=date.today() + timedelta(days=7),
                    status='pending'
                )
                db.session.add(promise)
                print(f"  ✅ Promesa creada para caso {case.id}: ${promise.amount}")
        
        db.session.commit()
        
        # Crear actividades
        print("\n📞 Creando actividades...")
        activity_types = ['call', 'email', 'visit', 'note']
        for i, case in enumerate(cases_created):
            # Crear 2-3 actividades por caso
            for j in range(2):
                activity = Activity(
                    case_id=case.id,
                    type=activity_types[i % len(activity_types)],
                    notes=f'Actividad de prueba {j+1} para {case.debtor_name}',
                    created_by_id=gestor.id if gestor else admin.id
                )
                db.session.add(activity)
            print(f"  ✅ {2} actividades creadas para caso {case.id}")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("✅ Datos de muestra creados exitosamente!")
        print("=" * 60)
        print(f"\n📊 Resumen:")
        print(f"  - Casos: {Case.query.count()}")
        print(f"  - Promesas: {Promise.query.count()}")
        print(f"  - Actividades: {Activity.query.count()}")
        print(f"  - Usuarios: {User.query.count()}")
        print("\n🎉 Ahora puedes ver datos reales en el dashboard!")
        print("   Inicia la app y haz login como 'admin'")
        print("=" * 60)


if __name__ == '__main__':
    try:
        create_sample_data()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

