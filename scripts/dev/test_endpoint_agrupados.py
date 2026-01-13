#!/usr/bin/env python3
"""
Script para probar el endpoint de casos agrupados por DNI.
"""
import sys
import os
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.services.dashboard import get_casos_agrupados_por_dni
from app.features.cases.models import Case

def test_endpoint():
    """Prueba el endpoint de casos agrupados."""
    app = create_app()
    
    with app.app_context():
        # Obtener casos agrupados
        grupos = get_casos_agrupados_por_dni(
            cartera_id=None,
            gestor_id=None,
            include_relations=False
        )
        
        print(f"\n{'='*60}")
        print(f"Total de grupos (clientes): {len(grupos)}")
        print(f"{'='*60}\n")
        
        # Buscar los DNIs específicos
        dni_buscados = ['20737173', '92452887']
        
        for dni in dni_buscados:
            grupo = next((g for g in grupos if g.get('dni') == dni), None)
            if grupo:
                print(f"DNI: {dni}")
                print(f"  Cliente: {grupo['cliente']['name']} {grupo['cliente']['lastname']}")
                print(f"  Total de deudas: {grupo['total_deudas']}")
                print(f"  Deuda consolidada: ${grupo['deuda_consolidada']:,.2f}")
                print(f"  Monto inicial total: ${grupo['monto_inicial_total']:,.2f}")
                print(f"\n  Deudas individuales:")
                for idx, deuda in enumerate(grupo['deudas'], 1):
                    print(f"    Deuda {idx}:")
                    print(f"      ID: {deuda.get('id')}")
                    print(f"      Nro Cliente: {deuda.get('nro_cliente')}")
                    print(f"      Total: ${deuda.get('total', 0):,.2f}")
                    print(f"      Monto Inicial: ${deuda.get('monto_inicial', 0) or 0:,.2f}")
                    print(f"      Fecha Último Pago: {deuda.get('fecha_ultimo_pago')}")
                    print(f"      Cartera: {deuda.get('cartera_nombre')}")
                    print(f"      Created At: {deuda.get('created_at')}")
                print(f"\n{'='*60}\n")
            else:
                print(f"DNI {dni} NO ENCONTRADO\n")
        
        # Verificar casos en BD directamente
        print("\nVerificación directa en BD:")
        print(f"{'='*60}\n")
        for dni in dni_buscados:
            casos = Case.query.filter_by(dni=dni).all()
            print(f"DNI {dni}: {len(casos)} casos en BD")
            for caso in casos:
                print(f"  - ID: {caso.id}, Nro Cliente: {caso.nro_cliente}, Total: ${caso.total}, Created: {caso.created_at}")

if __name__ == '__main__':
    test_endpoint()

