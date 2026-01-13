#!/usr/bin/env python3
"""
Script para probar qué retorna el backend con filtro de gestor.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.services.dashboard import get_casos_agrupados_por_dni

def test_backend():
    app = create_app()
    with app.app_context():
        # Probar con filtro de gestor (ID=2)
        print("=== CON FILTRO DE GESTOR 2 (sin cartera) ===")
        grupos = get_casos_agrupados_por_dni(cartera_id=None, gestor_id=2)
        grupo = next((g for g in grupos if g.get('dni') == '20737173'), None)
        if grupo:
            print(f"Grupo encontrado: DNI {grupo['dni']}")
            print(f"Total deudas: {len(grupo['deudas'])}")
            print(f"total_deudas: {grupo.get('total_deudas', 0)}")
            for i, deuda in enumerate(grupo['deudas'], 1):
                print(f"  Deuda {i}: ID={deuda.get('id')}, Nro Cliente={deuda.get('nro_cliente')}, Assigned To={deuda.get('assigned_to_id')}, Cartera ID={deuda.get('cartera_id')}")
        else:
            print("Grupo NO encontrado")
        
        print("\n=== CON FILTRO DE GESTOR 2 Y CARTERA 1 ===")
        grupos = get_casos_agrupados_por_dni(cartera_id=1, gestor_id=2)
        grupo = next((g for g in grupos if g.get('dni') == '20737173'), None)
        if grupo:
            print(f"Grupo encontrado: DNI {grupo['dni']}")
            print(f"Total deudas: {len(grupo['deudas'])}")
            print(f"total_deudas: {grupo.get('total_deudas', 0)}")
            for i, deuda in enumerate(grupo['deudas'], 1):
                print(f"  Deuda {i}: ID={deuda.get('id')}, Nro Cliente={deuda.get('nro_cliente')}, Assigned To={deuda.get('assigned_to_id')}, Cartera ID={deuda.get('cartera_id')}")
        else:
            print("Grupo NO encontrado")

if __name__ == '__main__':
    test_backend()

