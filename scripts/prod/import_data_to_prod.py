#!/usr/bin/env python3
"""
Script para importar datos exportados desde develop a producción.
Importa: carteras, case_statuses, casos, actividades, promesas.
NOTA: Los usuarios NO se importan (se mantienen los de producción).
"""
import sys
import os
import json
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.carteras.models import Cartera
from app.features.cases.models import Case, CaseStatus
from app.features.activities.models import Activity
from app.features.cases.promise import Promise

def parse_fecha(fecha_str):
    """Convierte fecha de formato ISO a objeto date."""
    if not fecha_str:
        return None
    try:
        return datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
    except:
        return None

def import_data(json_file='data/export_for_prod.json'):
    """Importa datos desde archivo JSON a producción."""
    app = create_app()
    
    with app.app_context():
        # Leer archivo JSON
        if not os.path.exists(json_file):
            print(f"[ERROR] No se encontró el archivo {json_file}")
            return
        
        print(f"[READ] Leyendo datos desde {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"[INFO] Datos exportados el: {data.get('exported_at', 'N/A')}\n")
        
        # 1. Importar carteras
        print("[IMPORT] Importando carteras...")
        carteras_importadas = 0
        carteras_map = {}  # Mapeo de ID antiguo -> ID nuevo
        for cartera_data in data.get('carteras', []):
            # Verificar si ya existe por nombre
            existing = Cartera.query.filter_by(nombre=cartera_data['nombre']).first()
            if existing:
                carteras_map[cartera_data['id']] = existing.id
                print(f"   [SKIP] Cartera '{cartera_data['nombre']}' ya existe (ID: {existing.id})")
            else:
                new_cartera = Cartera(
                    nombre=cartera_data['nombre'],
                    activo=cartera_data.get('activo', True)
                )
                db.session.add(new_cartera)
                db.session.flush()  # Para obtener el ID
                carteras_map[cartera_data['id']] = new_cartera.id
                carteras_importadas += 1
                print(f"   [OK] Cartera '{cartera_data['nombre']}' importada (ID: {new_cartera.id})")
        db.session.commit()
        print(f"   [SUCCESS] {carteras_importadas} carteras nuevas importadas\n")
        
        # 2. Importar case_statuses
        print("[IMPORT] Importando estados de caso...")
        statuses_importados = 0
        statuses_map = {}  # Mapeo de ID antiguo -> ID nuevo
        for status_data in data.get('case_statuses', []):
            # Verificar si ya existe por nombre
            existing = CaseStatus.query.filter_by(nombre=status_data['nombre']).first()
            if existing:
                statuses_map[status_data['id']] = existing.id
                print(f"   [SKIP] Estado '{status_data['nombre']}' ya existe (ID: {existing.id})")
            else:
                new_status = CaseStatus(
                    id=status_data['id'],  # Mantener ID original si es posible
                    nombre=status_data['nombre'],
                    activo=status_data.get('activo', True)
                )
                db.session.add(new_status)
                db.session.flush()
                statuses_map[status_data['id']] = new_status.id
                statuses_importados += 1
                print(f"   [OK] Estado '{status_data['nombre']}' importado (ID: {new_status.id})")
        db.session.commit()
        print(f"   [SUCCESS] {statuses_importados} estados nuevos importados\n")
        
        # 3. Importar casos
        print("[IMPORT] Importando casos...")
        casos_importados = 0
        casos_skipped = 0
        casos_map = {}  # Mapeo de nro_cliente -> ID nuevo (para actividades/promesas)
        for case_data in data.get('cases', []):
            # Verificar si ya existe por nro_cliente
            nro_cliente = case_data.get('nro_cliente')
            if nro_cliente:
                existing = Case.query.filter_by(nro_cliente=nro_cliente).first()
                if existing:
                    casos_map[nro_cliente] = existing.id
                    casos_skipped += 1
                    print(f"   [SKIP] Caso nro_cliente '{nro_cliente}' ya existe (ID: {existing.id}), saltando...")
                    continue
            
            # Mapear IDs de relaciones
            cartera_id = carteras_map.get(case_data.get('cartera_id'))
            status_id = statuses_map.get(case_data.get('status_id'), case_data.get('status_id', 1))
            
            if not cartera_id:
                print(f"   [WARN] Caso {nro_cliente}: cartera_id no encontrado, usando primera cartera disponible")
                primera_cartera = Cartera.query.first()
                if primera_cartera:
                    cartera_id = primera_cartera.id
                else:
                    print(f"   [ERROR] No hay carteras disponibles, saltando caso")
                    continue
            
            new_case = Case(
                nro_cliente=nro_cliente,
                name=case_data['name'],
                lastname=case_data['lastname'],
                dni=case_data.get('dni'),
                total=Decimal(str(case_data['total'])),
                monto_inicial=Decimal(str(case_data['monto_inicial'])) if case_data.get('monto_inicial') else None,
                fecha_ultimo_pago=parse_fecha(case_data.get('fecha_ultimo_pago')),
                telefono=case_data.get('telefono'),
                calle_nombre=case_data.get('calle_nombre'),
                calle_nro=case_data.get('calle_nro'),
                localidad=case_data.get('localidad'),
                cp=case_data.get('cp'),
                provincia=case_data.get('provincia'),
                status_id=status_id,
                cartera_id=cartera_id,
                assigned_to_id=case_data.get('assigned_to_id'),
                notes=case_data.get('notes')
            )
            db.session.add(new_case)
            db.session.flush()
            if nro_cliente:
                casos_map[nro_cliente] = new_case.id
            casos_importados += 1
            print(f"   [OK] Caso '{nro_cliente}' importado (ID: {new_case.id})")
        
        db.session.commit()
        print(f"   [SUCCESS] {casos_importados} casos nuevos importados, {casos_skipped} saltados (ya existían)\n")
        
        # 4. Crear mapeo de case_id antiguo -> nuevo usando nro_cliente
        # Necesitamos el case_id original del export para mapear actividades/promesas
        print("[MAP] Creando mapeo de case_id...")
        case_id_map = {}  # case_id_antiguo -> case_id_nuevo
        for case_data in data.get('cases', []):
            old_case_id = case_data.get('id')  # Si el export incluye el ID original
            nro_cliente = case_data.get('nro_cliente')
            if nro_cliente and nro_cliente in casos_map:
                # Si tenemos el ID antiguo en el export, lo mapeamos
                # Nota: El script de exportación no exporta el ID, así que usaremos nro_cliente
                pass
        
        # 4. Importar actividades
        print("[IMPORT] Importando actividades...")
        actividades_importadas = 0
        actividades_skipped = 0
        # Necesitamos mapear case_id usando nro_cliente
        # Como el export no incluye el case_id original, necesitamos buscar por nro_cliente
        # Para esto, necesitaríamos modificar el export para incluir el case_id original
        # Por ahora, intentamos buscar el caso por los datos disponibles
        for activity_data in data.get('activities', []):
            old_case_id = activity_data.get('case_id')
            # Buscar el caso en los datos exportados para obtener nro_cliente
            case_data = next((c for c in data.get('cases', []) if c.get('id') == old_case_id), None)
            if not case_data:
                actividades_skipped += 1
                continue
            
            nro_cliente = case_data.get('nro_cliente')
            if not nro_cliente:
                actividades_skipped += 1
                continue
            
            # Buscar el caso nuevo por nro_cliente
            new_case = Case.query.filter_by(nro_cliente=nro_cliente).first()
            if not new_case:
                actividades_skipped += 1
                continue
            
            new_activity = Activity(
                case_id=new_case.id,
                type=activity_data.get('type', 'note'),
                notes=activity_data.get('notes'),
                created_by_id=activity_data.get('created_by_id', 1)  # Default a admin
            )
            db.session.add(new_activity)
            actividades_importadas += 1
        
        db.session.commit()
        print(f"   [SUCCESS] {actividades_importadas} actividades importadas, {actividades_skipped} saltadas\n")
        
        # 5. Importar promesas
        print("[IMPORT] Importando promesas...")
        promesas_importadas = 0
        promesas_skipped = 0
        for promise_data in data.get('promises', []):
            old_case_id = promise_data.get('case_id')
            # Buscar el caso en los datos exportados
            case_data = next((c for c in data.get('cases', []) if c.get('id') == old_case_id), None)
            if not case_data:
                promesas_skipped += 1
                continue
            
            nro_cliente = case_data.get('nro_cliente')
            if not nro_cliente:
                promesas_skipped += 1
                continue
            
            # Buscar el caso nuevo por nro_cliente
            new_case = Case.query.filter_by(nro_cliente=nro_cliente).first()
            if not new_case:
                promesas_skipped += 1
                continue
            
            new_promise = Promise(
                case_id=new_case.id,
                amount=Decimal(str(promise_data.get('amount', 0))),
                promise_date=parse_fecha(promise_data.get('promise_date')),
                status=promise_data.get('status', 'pending'),
                fulfilled_date=parse_fecha(promise_data.get('fulfilled_date')),
                notes=promise_data.get('notes')
            )
            db.session.add(new_promise)
            promesas_importadas += 1
        
        db.session.commit()
        print(f"   [SUCCESS] {promesas_importadas} promesas importadas, {promesas_skipped} saltadas\n")
        
        print("[SUCCESS] Importación completada!")
        print(f"\n[SUMMARY] Resumen:")
        print(f"   - Carteras: {carteras_importadas} nuevas")
        print(f"   - Estados: {statuses_importados} nuevos")
        print(f"   - Casos: {casos_importados} nuevos, {casos_skipped} saltados")
        print(f"   - Actividades: {actividades_importadas} importadas, {actividades_skipped} saltadas")
        print(f"   - Promesas: {promesas_importadas} importadas, {promesas_skipped} saltadas")

if __name__ == '__main__':
    import_data()

