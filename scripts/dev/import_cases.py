#!/usr/bin/env python3
"""
Script para importar casos desde datos tabulares.
"""
import sys
import os
from decimal import Decimal
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.cases.models import Case, CaseStatus
from app.features.carteras.models import Cartera

# Datos de casos a importar
CASES_DATA = [
    {
        'nro_cliente': '332412',
        'dni': '20737173',
        'calle_nombre': '75',
        'calle_nro': '1675',
        'localidad': 'NECOCHEA',
        'provincia': 'BUENOS AIRES',
        'cp': '7630',
        'name': 'CAROLINA',
        'lastname': 'ALDABE',
        'monto_inicial': '500000.00',
        'total': '918372.00',
        'fecha_ultimo_pago': '10/5/2024',
        'telefono': '2262474992'
    },
    {
        'nro_cliente': '351810',
        'dni': '28126091',
        'calle_nombre': '25 DE MAYO ENTRE URUGUAY Y PARANA',
        'calle_nro': '3548',
        'localidad': 'BAHIA BLANCA',
        'provincia': 'BUENOS AIRES',
        'cp': '8000',
        'name': 'VANESSA ESTER',
        'lastname': 'BARROS',
        'monto_inicial': '600000.00',
        'total': '1492098.00',
        'fecha_ultimo_pago': '10/5/2024',
        'telefono': '2932526218'
    },
    {
        'nro_cliente': '345075',
        'dni': '30564727',
        'calle_nombre': 'LATANZIO',
        'calle_nro': '888',
        'localidad': 'BAHIA BLANCA',
        'provincia': 'BUENOS AIRES',
        'cp': '8000',
        'name': 'HORACIO ANDRES',
        'lastname': 'CHIAPPA',
        'monto_inicial': '500000.00',
        'total': '1377558.00',
        'fecha_ultimo_pago': '10/4/2024',
        'telefono': '2914395295'
    },
    {
        'nro_cliente': '350135',
        'dni': '32585228',
        'calle_nombre': '73',
        'calle_nro': '3504',
        'localidad': 'NECOCHEA',
        'provincia': 'BUENOS AIRES',
        'cp': '7630',
        'name': 'EMANUEL ALEJANDRO',
        'lastname': 'MARQUEZ',
        'monto_inicial': '400000.00',
        'total': '1084005.00',
        'fecha_ultimo_pago': '10/5/2024',
        'telefono': '2262242058'
    },
    {
        'nro_cliente': '334403',
        'dni': '34005512',
        'calle_nombre': 'ALVARADO',
        'calle_nro': '287',
        'localidad': 'BAHIA BLANCA',
        'provincia': 'BUENOS AIRES',
        'cp': '8000',
        'name': 'SOLEDAD DEL VALLE',
        'lastname': 'ABAN',
        'monto_inicial': '300000.00',
        'total': '1001928.00',
        'fecha_ultimo_pago': '10/2/2024',
        'telefono': '2915014505'
    },
    {
        'nro_cliente': '331955',
        'dni': '92452887',
        'calle_nombre': 'MONTEVIDEO',
        'calle_nro': '555',
        'localidad': 'BAHIA BLANCA',
        'provincia': 'BUENOS AIRES',
        'cp': '8000',
        'name': 'RUBEN ALBERTO',
        'lastname': 'GARCES SALAZAR',
        'monto_inicial': '200000.00',
        'total': '306120.00',
        'fecha_ultimo_pago': '10/6/2024',
        'telefono': '2914752382'
    },
    # Casos duplicados (mismo DNI, diferente nro_cliente)
    {
        'nro_cliente': '347337',
        'dni': '20737173',
        'calle_nombre': '75',
        'calle_nro': '1675',
        'localidad': 'NECOCHEA',
        'provincia': 'BUENOS AIRES',
        'cp': '7630',
        'name': 'CAROLINA',
        'lastname': 'ALDABE',
        'monto_inicial': '400000.00',
        'total': '979592.00',
        'fecha_ultimo_pago': '10/5/2024',
        'telefono': '2262474992'
    },
    {
        'nro_cliente': '348460',
        'dni': '92452887',
        'calle_nombre': 'MONTEVIDEO',
        'calle_nro': '555',
        'localidad': 'BAHIA BLANCA',
        'provincia': 'BUENOS AIRES',
        'cp': '8000',
        'name': 'RUBEN ALBERTO',
        'lastname': 'GARCES SALAZAR',
        'monto_inicial': '500000.00',
        'total': '1475804.00',
        'fecha_ultimo_pago': '10/6/2024',
        'telefono': '2914752382'
    }
]


def parse_date(date_str):
    """Parsea fecha en formato DD/MM/YYYY o MM/DD/YYYY."""
    if not date_str:
        return None
    try:
        # Intentar formato DD/MM/YYYY primero (más común en Argentina)
        return datetime.strptime(date_str, '%d/%m/%Y').date()
    except ValueError:
        try:
            # Intentar formato MM/DD/YYYY
            return datetime.strptime(date_str, '%m/%d/%Y').date()
        except ValueError:
            return None


def parse_amount(amount_str):
    """Parsea monto removiendo símbolos de moneda y espacios."""
    if not amount_str:
        return None
    # Remover $, espacios, comas y puntos de miles
    # Formato puede ser: "$  400,000.00" o "400000.00"
    cleaned = amount_str.replace('$', '').replace(' ', '').strip()
    # Si tiene comas, asumir formato con punto decimal: "400,000.00" -> "400000.00"
    if ',' in cleaned and '.' in cleaned:
        # Formato: "400,000.00" -> quitar comas
        cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Formato: "400,000" -> podría ser miles o decimales
        # Si hay más de 3 dígitos después de la coma, es decimal (formato europeo)
        parts = cleaned.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Es decimal con coma: "400,50" -> "400.50"
            cleaned = parts[0] + '.' + parts[1]
        else:
            # Es miles: "400,000" -> "400000"
            cleaned = cleaned.replace(',', '')
    try:
        return Decimal(cleaned)
    except:
        return None


def import_cases():
    """Importa los casos a la base de datos."""
    app = create_app()
    
    with app.app_context():
        # Obtener estado por defecto (Sin Arreglo)
        default_status = CaseStatus.query.filter_by(nombre='Sin Arreglo', activo=True).first()
        if not default_status:
            print("ERROR: No se encontró el estado 'Sin Arreglo'. Creando...")
            default_status = CaseStatus(id=1, nombre='Sin Arreglo', activo=True)
            db.session.add(default_status)
            db.session.commit()
        
        # Obtener primera cartera activa
        cartera = Cartera.query.filter_by(activo=True).first()
        if not cartera:
            print("ERROR: No se encontró ninguna cartera activa. Creando 'Cristal Cash'...")
            cartera = Cartera(nombre='Cristal Cash', activo=True)
            db.session.add(cartera)
            db.session.commit()
        
        print(f"Usando cartera: {cartera.nombre} (ID: {cartera.id})")
        print(f"Usando estado: {default_status.nombre} (ID: {default_status.id})")
        print(f"\nImportando {len(CASES_DATA)} casos...\n")
        
        imported = 0
        skipped = 0
        
        for case_data in CASES_DATA:
            # Verificar si el caso ya existe por nro_cliente
            existing = Case.query.filter_by(nro_cliente=case_data['nro_cliente']).first()
            if existing:
                print(f"[SKIP] Caso {case_data['nro_cliente']} ya existe, saltando...")
                skipped += 1
                continue
            
            # Parsear datos
            monto_inicial = parse_amount(case_data['monto_inicial'])
            total = parse_amount(case_data['total'])
            fecha_ultimo_pago = parse_date(case_data['fecha_ultimo_pago'])
            
            # Crear caso
            case = Case(
                nro_cliente=case_data['nro_cliente'],
                dni=case_data['dni'],
                name=case_data['name'],
                lastname=case_data['lastname'],
                calle_nombre=case_data['calle_nombre'],
                calle_nro=case_data['calle_nro'],
                localidad=case_data['localidad'],
                provincia=case_data['provincia'],
                cp=case_data['cp'],
                telefono=case_data['telefono'],
                monto_inicial=monto_inicial,
                total=total if total else Decimal('0'),
                fecha_ultimo_pago=fecha_ultimo_pago,
                status_id=default_status.id,
                cartera_id=cartera.id,
            )
            
            db.session.add(case)
            imported += 1
            print(f"[OK] Caso {case_data['nro_cliente']} - {case_data['name']} {case_data['lastname']} agregado")
        
        db.session.commit()
        print(f"\n[OK] Importacion completada: {imported} casos importados, {skipped} saltados")


if __name__ == '__main__':
    import_cases()

