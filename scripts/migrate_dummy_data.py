#!/usr/bin/env python3
"""
Script para migrar datos dummy del dashboard-gestor.js a la base de datos.
"""
import sys
import re
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.db import db
from app.models import User, Case, Promise, Activity


# Datos dummy extraídos del dashboard-gestor.js
DUMMY_DATA = {
    'favacard': [
        {
            'nombre': 'Carlos Mendoza',
            'dni': '12.345.678',
            'numeroId': 'FAV-001',
            'telefono': '+54 11 4567-8901',
            'email': 'carlos.mendoza@email.com',
            'direccion': 'Av. Corrientes 1234, CABA',
            'montoAdeudado': 125000,
            'fechaVencimiento': '15/12/2023',
            'ultimaGestion': '05/01/2024',
            'entidadFinanciera': 'Banco Nacional S.A.',
            'observaciones': 'Cliente con historial de pagos irregular. Última cuota pagada hace 6 meses. Presenta disposición a negociar.',
            'estado': 'contactado',
            'diasMora': 45,
        },
        {
            'nombre': 'María Rodríguez',
            'dni': '23.456.789',
            'numeroId': 'FAV-002',
            'telefono': '+54 11 5234-5678',
            'email': 'maria.rodriguez@email.com',
            'direccion': 'Libertador 5678, CABA',
            'montoAdeudado': 85000,
            'fechaVencimiento': '10/11/2023',
            'ultimaGestion': '02/01/2024',
            'entidadFinanciera': 'Banco Nacional S.A.',
            'observaciones': 'Cliente comunicativa. Ha realizado pagos parciales. Negociación en curso.',
            'estado': 'con-arreglo',
            'diasMora': 60,
        },
        {
            'nombre': 'Luis Fernández',
            'dni': '34.567.890',
            'numeroId': 'FAV-003',
            'telefono': '+54 11 4789-1234',
            'email': 'luis.fernandez@email.com',
            'direccion': 'Rivadavia 9876, CABA',
            'montoAdeudado': 95000,
            'fechaVencimiento': '20/12/2023',
            'ultimaGestion': '28/12/2023',
            'entidadFinanciera': 'Banco Nacional S.A.',
            'observaciones': 'Primer contacto pendiente. Cliente no responde llamadas.',
            'estado': 'sin-gestion',
            'diasMora': 50,
        },
        {
            'nombre': 'Ana Martínez',
            'dni': '45.678.901',
            'numeroId': 'FAV-004',
            'telefono': '+54 11 5123-4567',
            'email': 'ana.martinez@email.com',
            'direccion': 'Córdoba 2345, CABA',
            'montoAdeudado': 67000,
            'fechaVencimiento': '05/11/2023',
            'ultimaGestion': '01/01/2024',
            'entidadFinanciera': 'Banco Nacional S.A.',
            'observaciones': 'Deuda antigua. Cliente con problemas económicos. Evaluar situación.',
            'estado': 'contactado',
            'diasMora': 70,
        }
    ],
    'naldo': [
        {
            'nombre': 'Roberto Silva',
            'dni': '56.789.012',
            'numeroId': 'NAL-001',
            'telefono': '+54 11 4567-8901',
            'email': 'roberto.silva@email.com',
            'direccion': 'Santa Fe 3456, CABA',
            'montoAdeudado': 145000,
            'fechaVencimiento': '18/12/2023',
            'ultimaGestion': '04/01/2024',
            'entidadFinanciera': 'Naldo Finanzas',
            'observaciones': 'Cliente con trabajo estable. Muestra interés en regularizar situación.',
            'estado': 'contactado',
            'diasMora': 55,
        },
        {
            'nombre': 'Patricia López',
            'dni': '67.890.123',
            'numeroId': 'NAL-002',
            'telefono': '+54 11 5234-5678',
            'email': 'patricia.lopez@email.com',
            'direccion': 'Florida 4567, CABA',
            'montoAdeudado': 98000,
            'fechaVencimiento': '22/11/2023',
            'ultimaGestion': '03/01/2024',
            'entidadFinanciera': 'Naldo Finanzas',
            'observaciones': 'Cliente ha cumplido con promesas anteriores. Plan de pago activo.',
            'estado': 'con-arreglo',
            'diasMora': 65,
        },
        {
            'nombre': 'Jorge García',
            'dni': '78.901.234',
            'numeroId': 'NAL-003',
            'telefono': '+54 11 4789-1234',
            'email': 'jorge.garcia@email.com',
            'direccion': 'Lavalle 7890, CABA',
            'montoAdeudado': 180000,
            'fechaVencimiento': '30/12/2023',
            'ultimaGestion': '15/12/2023',
            'entidadFinanciera': 'Naldo Finanzas',
            'observaciones': 'Cliente elusivo. No responde comunicación. Considerar incobrable.',
            'estado': 'incobrable',
            'diasMora': 40,
        },
        {
            'nombre': 'Sofía Herrera',
            'dni': '89.012.345',
            'numeroId': 'NAL-004',
            'telefono': '+54 11 5123-4567',
            'email': 'sofia.herrera@email.com',
            'direccion': 'Alvear 1234, CABA',
            'montoAdeudado': 72000,
            'fechaVencimiento': '12/11/2023',
            'ultimaGestion': '29/12/2023',
            'entidadFinanciera': 'Naldo Finanzas',
            'observaciones': 'Cliente regulariza deuda. Últimos pagos al día. Seguimiento continuo.',
            'estado': 'con-arreglo',
            'diasMora': 75,
        }
    ],
    'naranjax': [
        {
            'nombre': 'Diego Torres',
            'dni': '90.123.456',
            'numeroId': 'NAR-001',
            'telefono': '+54 11 4456-7890',
            'email': 'diego.torres@email.com',
            'direccion': 'Cabildo 5678, CABA',
            'montoAdeudado': 110000,
            'fechaVencimiento': '25/12/2023',
            'ultimaGestion': '06/01/2024',
            'entidadFinanciera': 'NaranjaX S.A.',
            'observaciones': 'Cliente negocia activamente. Propuestas de pago en evaluación.',
            'estado': 'contactado',
            'diasMora': 48,
        },
        {
            'nombre': 'Laura Díaz',
            'dni': '01.234.567',
            'numeroId': 'NAR-002',
            'telefono': '+54 11 5345-6789',
            'email': 'laura.diaz@email.com',
            'direccion': 'San Martín 9012, CABA',
            'montoAdeudado': 83000,
            'fechaVencimiento': '08/11/2023',
            'ultimaGestion': '30/12/2023',
            'entidadFinanciera': 'NaranjaX S.A.',
            'observaciones': 'Casos cerrados. Cliente de baja del sistema.',
            'estado': 'de-baja',
            'diasMora': 80,
        }
    ]
}


def parse_date(date_str):
    """Parsea fecha en formato DD/MM/YYYY."""
    try:
        day, month, year = map(int, date_str.split('/'))
        return date(year, month, day)
    except:
        return None


def map_estado_to_status(estado):
    """Mapea estados del frontend a estados de la BD."""
    mapping = {
        'sin-gestion': 'en_gestion',
        'contactado': 'en_gestion',
        'con-arreglo': 'promesa',
        'incobrable': 'incobrable',
        'de-baja': 'incobrable',
        'pagada': 'pagada'
    }
    return mapping.get(estado, 'en_gestion')


def migrate_dummy_data():
    """Migra los datos dummy a la base de datos."""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("MIGRACION DE DATOS DUMMY A BASE DE DATOS")
        print("=" * 60)
        
        # Obtener o crear gestor
        gestor = User.query.filter_by(username='gestor', role='gestor').first()
        if not gestor:
            print("  [WARN] No se encontro usuario 'gestor', creando...")
            gestor = User(username='gestor', role='gestor', active=True)
            gestor.set_password('gestor123')
            db.session.add(gestor)
            db.session.commit()
            print("  [OK] Usuario gestor creado")
        
        total_casos = 0
        total_promesas = 0
        total_actividades = 0
        
        # Mapeo de carteras
        cartera_mapping = {
            'favacard': 'Cartera A',
            'naldo': 'Cartera B',
            'naranjax': 'Cartera C'
        }
        
        # Procesar cada cartera
        for cartera_key, cartera_name in cartera_mapping.items():
            print(f"\n[INFO] Procesando cartera: {cartera_name} ({cartera_key})")
            
            clientes = DUMMY_DATA.get(cartera_key, [])
            
            for cliente_data in clientes:
                # Verificar si el caso ya existe (por DNI)
                dni_clean = cliente_data['dni'].replace('.', '').replace('-', '')
                existing_case = Case.query.filter(
                    Case.dni.like(f'%{dni_clean}%')
                ).first()
                
                if existing_case:
                    print(f"  [SKIP] Caso ya existe: {cliente_data['nombre']} (DNI: {cliente_data['dni']})")
                    continue
                
                # Crear caso
                case = Case(
                    entity=cliente_data['entidadFinanciera'],
                    debtor_name=cliente_data['nombre'],
                    dni=cliente_data['dni'],
                    amount=Decimal(str(cliente_data['montoAdeudado'])),
                    status=map_estado_to_status(cliente_data['estado']),
                    cartera=cartera_name,
                    assigned_to_id=gestor.id,
                    notes=f"{cliente_data['observaciones']}\n\nContacto: {cliente_data['telefono']}\nEmail: {cliente_data['email']}\nDirección: {cliente_data['direccion']}\nID: {cliente_data['numeroId']}"
                )
                
                db.session.add(case)
                db.session.flush()  # Para obtener el ID
                total_casos += 1
                
                print(f"  [OK] Caso creado: {cliente_data['nombre']} - ${cliente_data['montoAdeudado']}")
                
                # Crear promesa si el estado es 'con-arreglo'
                if cliente_data['estado'] == 'con-arreglo':
                    # Calcular fecha de promesa (7 días desde hoy)
                    promise_date = date.today()
                    
                    promise = Promise(
                        case_id=case.id,
                        amount=Decimal(str(cliente_data['montoAdeudado'] * 0.5)),  # 50% del monto
                        promise_date=promise_date,
                        status='pending',
                        notes='Promesa creada desde migración de datos dummy'
                    )
                    db.session.add(promise)
                    total_promesas += 1
                    print(f"    [OK] Promesa creada: ${promise.amount}")
                
                # Crear actividad de última gestión
                if cliente_data.get('ultimaGestion'):
                    gestion_date = parse_date(cliente_data['ultimaGestion'])
                    if gestion_date:
                        activity = Activity(
                            case_id=case.id,
                            type='call',
                            notes=f"Última gestión registrada: {cliente_data['ultimaGestion']}",
                            created_by_id=gestor.id,
                            created_at=datetime.combine(gestion_date, datetime.min.time())
                        )
                        db.session.add(activity)
                        total_actividades += 1
                        print(f"    [OK] Actividad creada: {cliente_data['ultimaGestion']}")
        
        # Commit final
        try:
            db.session.commit()
            print("\n" + "=" * 60)
            print("[OK] MIGRACION COMPLETADA")
            print("=" * 60)
            print(f"  Casos creados: {total_casos}")
            print(f"  Promesas creadas: {total_promesas}")
            print(f"  Actividades creadas: {total_actividades}")
            print("\n[OK] Los datos dummy han sido migrados a la base de datos.")
            print("     Ahora puedes verlos en el dashboard admin y en SQLite Viewer.")
            print("=" * 60)
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Error al guardar: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0


if __name__ == '__main__':
    try:
        exit_code = migrate_dummy_data()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

