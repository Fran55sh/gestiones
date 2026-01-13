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
from app.features.cases.models import Case, CaseStatus
from app.features.cases.promise import Promise
from app.features.activities.models import Activity
from app.features.carteras.models import Cartera


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
        
        # Get or create carteras
        cartera_a = Cartera.query.filter_by(nombre='Cristal Cash').first()
        if not cartera_a:
            cartera_a = Cartera(nombre='Cristal Cash', activo=True)
            db.session.add(cartera_a)
            print("  ✅ Cartera 'Cristal Cash' creada")

        cartera_b = Cartera.query.filter_by(nombre='Favacard').first()
        if not cartera_b:
            cartera_b = Cartera(nombre='Favacard', activo=True)
            db.session.add(cartera_b)
            print("  ✅ Cartera 'Favacard' creada")
        db.session.commit()
        
        # Get or create case statuses
        status_sin_arreglo = CaseStatus.query.filter_by(nombre='Sin Arreglo').first()
        status_en_gestion = CaseStatus.query.filter_by(nombre='En gestión').first()
        status_con_arreglo = CaseStatus.query.filter_by(nombre='Con Arreglo').first()
        status_contactado = CaseStatus.query.filter_by(nombre='Contactado').first()
        status_incobrable = CaseStatus.query.filter_by(nombre='Incobrable').first()
        
        if not status_sin_arreglo:
            status_sin_arreglo = CaseStatus(nombre='Sin Arreglo', activo=True)
            db.session.add(status_sin_arreglo)
        if not status_en_gestion:
            status_en_gestion = CaseStatus(nombre='En gestión', activo=True)
            db.session.add(status_en_gestion)
        if not status_con_arreglo:
            status_con_arreglo = CaseStatus(nombre='Con Arreglo', activo=True)
            db.session.add(status_con_arreglo)
        if not status_contactado:
            status_contactado = CaseStatus(nombre='Contactado', activo=True)
            db.session.add(status_contactado)
        if not status_incobrable:
            status_incobrable = CaseStatus(nombre='Incobrable', activo=True)
            db.session.add(status_incobrable)
        db.session.commit()
        
        # Crear casos de ejemplo
        cases_data = [
            {
                'name': 'Carlos',
                'lastname': 'Rodríguez',
                'dni': '12345678',
                'nro_cliente': 'CLI-001',
                'total': Decimal('50000.00'),
                'fecha_ultimo_pago': date.today() - timedelta(days=30),
                'status_id': status_con_arreglo.id,
                'cartera_id': cartera_a.id,
                'assigned_to_id': gestor.id,
                'notes': 'Cliente contactado, acuerdo de pago establecido'
            },
            {
                'name': 'María',
                'lastname': 'González',
                'dni': '23456789',
                'nro_cliente': 'CLI-002',
                'total': Decimal('75000.00'),
                'fecha_ultimo_pago': None,
                'status_id': status_en_gestion.id,
                'cartera_id': cartera_a.id,
                'assigned_to_id': gestor.id,
                'notes': 'En proceso de contacto'
            },
            {
                'name': 'Pedro',
                'lastname': 'Martínez',
                'dni': '34567890',
                'nro_cliente': 'CLI-003',
                'total': Decimal('30000.00'),
                'fecha_ultimo_pago': date.today() - timedelta(days=15),
                'status_id': status_contactado.id,
                'cartera_id': cartera_b.id,
                'assigned_to_id': gestor.id,
                'notes': 'Contactado, esperando respuesta'
            },
            {
                'name': 'Ana',
                'lastname': 'López',
                'dni': '45678901',
                'nro_cliente': 'CLI-004',
                'total': Decimal('100000.00'),
                'fecha_ultimo_pago': None,
                'status_id': status_sin_arreglo.id,
                'cartera_id': cartera_b.id,
                'assigned_to_id': gestor.id,
                'notes': 'Sin contacto aún'
            },
            {
                'name': 'Luis',
                'lastname': 'Fernández',
                'dni': '56789012',
                'nro_cliente': 'CLI-005',
                'total': Decimal('25000.00'),
                'fecha_ultimo_pago': date.today() - timedelta(days=60),
                'status_id': status_con_arreglo.id,
                'cartera_id': cartera_a.id,
                'assigned_to_id': gestor.id,
                'notes': 'Pago parcial realizado'
            },
        ]
        
        cases_created = []
        for case_data in cases_data:
            # Verificar si el caso ya existe
            existing = Case.query.filter_by(
                name=case_data['name'],
                lastname=case_data['lastname'],
                dni=case_data['dni']
            ).first()
            
            if not existing:
                case = Case(
                    name=case_data['name'],
                    lastname=case_data['lastname'],
                    dni=case_data['dni'],
                    nro_cliente=case_data.get('nro_cliente'),
                    total=case_data['total'],
                    fecha_ultimo_pago=case_data['fecha_ultimo_pago'],
                    status_id=case_data['status_id'],
                    cartera_id=case_data['cartera_id'],
                    assigned_to_id=case_data['assigned_to_id'],
                    notes=case_data['notes']
                )
                db.session.add(case)
                cases_created.append(case)
                print(f"  ✅ Caso creado: {case_data['name']} {case_data['lastname']}")
        
        db.session.commit()
        
        # Crear algunas promesas de pago
        if cases_created:
            for case in cases_created[:3]:  # Solo para los primeros 3 casos
                promise = Promise(
                    case_id=case.id,
                    amount=case.total * Decimal('0.5'),  # 50% del total
                    promise_date=date.today() + timedelta(days=30),
                    status='pending',
                    notes='Primera cuota acordada'
                )
                db.session.add(promise)
                print(f"  ✅ Promesa creada para caso {case.id}")
        
        db.session.commit()
        
        # Crear algunas actividades
        if cases_created:
            for case in cases_created[:2]:  # Solo para los primeros 2 casos
                activity = Activity(
                    case_id=case.id,
                    type='call',
                    notes='Llamada realizada, sin respuesta',
                    created_by_id=gestor.id
                )
                db.session.add(activity)
                print(f"  ✅ Actividad creada para caso {case.id}")
        
        db.session.commit()
        
        print(f"\n✅ Datos de muestra creados exitosamente!")
        print(f"   - {len(cases_created)} casos creados")
        print(f"   - {len(cases_created[:3])} promesas creadas")
        print(f"   - {len(cases_created[:2])} actividades creadas")


if __name__ == '__main__':
    create_sample_data()
