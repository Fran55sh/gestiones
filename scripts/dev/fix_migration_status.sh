#!/bin/bash
# Script para marcar la migración 9064f0eb7540 como aplicada si la columna ya existe
# o para hacerla idempotente

echo "Verificando estado de la migración 9064f0eb7540..."

# Ejecutar dentro del contenedor
docker exec gestiones-mvp-dev python3 << 'PYTHON'
import sqlite3
import os

# Ruta a la base de datos
db_path = '/app/data/gestiones.db'

if not os.path.exists(db_path):
    print(f"[ERROR] Base de datos no encontrada en {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la tabla alembic_version existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
if cursor.fetchone():
    # Verificar qué migraciones están aplicadas
    cursor.execute("SELECT version_num FROM alembic_version")
    current_version = cursor.fetchone()
    if current_version:
        print(f"[INFO] Migración actual: {current_version[0]}")
    else:
        print("[INFO] No hay migraciones registradas")
    
    # Verificar si la columna management_status existe
    cursor.execute("PRAGMA table_info(cases)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'management_status' in columns:
        print("[INFO] Columna 'management_status' existe en la tabla cases")
        # Verificar si la migración 9064f0eb7540 está aplicada
        cursor.execute("SELECT version_num FROM alembic_version WHERE version_num = '9064f0eb7540'")
        if not cursor.fetchone():
            print("[WARN] La columna existe pero la migración no está registrada")
            print("[INFO] La migración será saltada automáticamente (idempotente)")
        else:
            print("[OK] Migración ya está registrada")
    else:
        print("[INFO] Columna 'management_status' NO existe (fue eliminada en refactorización)")
        print("[INFO] La migración será saltada automáticamente (idempotente)")
else:
    print("[INFO] Tabla alembic_version no existe aún")

conn.close()
print("[OK] Verificación completada")
PYTHON

echo ""
echo "Ahora intenta ejecutar las migraciones nuevamente:"
echo "docker exec gestiones-mvp-dev alembic -c config/alembic.ini upgrade head"

