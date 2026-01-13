#!/usr/bin/env python3
"""
Script para actualizar las fechas de último pago en la base de datos.
"""
import sys
import os
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.core.database import db
from app.features.cases.models import Case

# Datos a actualizar: nro_cliente -> fecha_ultimo_pago (formato MM/DD/YYYY)
FECHAS_CORRECTAS = {
    '332412': '10/5/2024',   # 5 de octubre de 2024
    '347337': '10/5/2024',   # 5 de octubre de 2024
    '351810': '10/5/2024',   # 5 de octubre de 2024
    '345075': '10/4/2024',   # 4 de octubre de 2024
    '350135': '10/5/2024',   # 5 de octubre de 2024
    '334403': '10/2/2024',   # 2 de octubre de 2024
    '331955': '10/6/2024',  # 6 de octubre de 2024
    '348460': '10/6/2024',   # 6 de octubre de 2024
}

def parse_fecha(fecha_str):
    """Convierte fecha de formato DD/MM/YYYY a objeto date."""
    try:
        # Parsear DD/MM/YYYY (formato europeo)
        partes = fecha_str.split('/')
        if len(partes) != 3:
            raise ValueError(f"Formato de fecha inválido: {fecha_str}")
        
        dia = int(partes[0])  # Primer número es el día
        mes = int(partes[1])  # Segundo número es el mes
        año = int(partes[2])  # Tercer número es el año
        
        return datetime(año, mes, dia).date()
    except Exception as e:
        print(f"Error parseando fecha {fecha_str}: {e}")
        return None

def update_fechas():
    """Actualiza las fechas de último pago en la base de datos."""
    app = create_app()
    
    with app.app_context():
        actualizados = 0
        errores = 0
        
        for nro_cliente, fecha_str in FECHAS_CORRECTAS.items():
            try:
                # Buscar el caso por nro_cliente
                caso = Case.query.filter_by(nro_cliente=nro_cliente).first()
                
                if not caso:
                    print(f"[ERROR] No se encontró caso con nro_cliente: {nro_cliente}")
                    errores += 1
                    continue
                
                # Parsear la fecha
                fecha_date = parse_fecha(fecha_str)
                if not fecha_date:
                    print(f"[ERROR] No se pudo parsear fecha para nro_cliente {nro_cliente}: {fecha_str}")
                    errores += 1
                    continue
                
                # Mostrar fecha actual y nueva
                fecha_actual = caso.fecha_ultimo_pago
                print(f"[INFO] Caso {nro_cliente} (ID: {caso.id}):")
                print(f"       Fecha actual: {fecha_actual}")
                print(f"       Fecha nueva:  {fecha_date} ({fecha_str})")
                
                # Actualizar
                caso.fecha_ultimo_pago = fecha_date
                actualizados += 1
                
            except Exception as e:
                print(f"[ERROR] Error actualizando caso {nro_cliente}: {e}")
                errores += 1
                continue
        
        # Guardar cambios
        if actualizados > 0:
            try:
                db.session.commit()
                print(f"\n[OK] {actualizados} casos actualizados correctamente")
            except Exception as e:
                db.session.rollback()
                print(f"\n[ERROR] Error al guardar cambios: {e}")
                errores += actualizados
                actualizados = 0
        
        if errores > 0:
            print(f"[WARN] {errores} errores encontrados")
        
        print(f"\n[RESUMEN] Actualizados: {actualizados}, Errores: {errores}")

if __name__ == '__main__':
    update_fechas()

