#!/usr/bin/env python3
"""
Script para probar qué retorna el backend para el DNI 20737173.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.services.dashboard import get_casos_agrupados_por_dni

def test_backend():
    app = create_app()
    with app.app_context():
        # Probar sin filtro de cartera
        print("=== SIN FILTRO DE CARTERA ===")
        grupos = get_casos_agrupados_por_dni(cartera_id=None, gestor_id=None)
        grupo = next((g for g in grupos if g.get('dni') == '20737173'), None)
        if grupo:
            print(f"Grupo encontrado: DNI {grupo['dni']}")
            print(f"Total deudas: {len(grupo['deudas'])}")
            print(f"total_deudas: {grupo.get('total_deudas', 0)}")
            for i, deuda in enumerate(grupo['deudas'], 1):
                print(f"  Deuda {i}: ID={deuda.get('id')}, Nro Cliente={deuda.get('nro_cliente')}, Cartera ID={deuda.get('cartera_id')}")
        else:
            print("Grupo NO encontrado")
        
        print("\n=== CON FILTRO DE CARTERA 1 ===")
        grupos = get_casos_agrupados_por_dni(cartera_id=1, gestor_id=None)
        grupo = next((g for g in grupos if g.get('dni') == '20737173'), None)
        if grupo:
            print(f"Grupo encontrado: DNI {grupo['dni']}")
            print(f"Total deudas: {len(grupo['deudas'])}")
            print(f"total_deudas: {grupo.get('total_deudas', 0)}")
            for i, deuda in enumerate(grupo['deudas'], 1):
                print(f"  Deuda {i}: ID={deuda.get('id')}, Nro Cliente={deuda.get('nro_cliente')}, Cartera ID={deuda.get('cartera_id')}")
        else:
            print("Grupo NO encontrado")

if __name__ == '__main__':
    test_backend()

