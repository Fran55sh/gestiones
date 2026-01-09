#!/usr/bin/env python3
"""
Script para verificar que la configuración está correcta.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias...")
    required = [
        'flask',
        'flask_sqlalchemy',
        'alembic',
        'flask_limiter',
        'flask_compress',
        'werkzeug',
        'pytest'
    ]
    
    missing = []
    for dep in required:
        try:
            __import__(dep.replace('-', '_'))
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} - NO INSTALADO")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠️  Faltan dependencias: {', '.join(missing)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False
    return True

def check_database():
    """Verifica que la base de datos pueda crearse."""
    print("\n🗄️  Verificando base de datos...")
    
    # Cambiar al directorio del proyecto
    original_dir = os.getcwd()
    try:
        os.chdir(project_root)
        
        from app import create_app
        from app.db import db
        
        app = create_app()
        with app.app_context():
            # Verificar que las tablas pueden crearse
            db.create_all()
            print("  ✅ Base de datos configurada correctamente")
            
            # Verificar usuarios por defecto
            from app.models import User
            users = User.query.all()
            print(f"  ✅ {len(users)} usuarios encontrados")
            
            if len(users) == 0:
                print("  ⚠️  No hay usuarios. Se crearán al iniciar la app.")
            
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        os.chdir(original_dir)

def check_config():
    """Verifica configuración básica."""
    print("\n⚙️  Verificando configuración...")
    
    # Verificar secret key
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key or secret_key.startswith('change-me'):
        print("  ⚠️  SECRET_KEY no configurada (usando valor por defecto)")
        print("     Configura SECRET_KEY en producción")
    else:
        print("  ✅ SECRET_KEY configurada")
    
    # Verificar directorio de datos
    data_dir = project_root / 'data'
    if not data_dir.exists():
        print("  ⚠️  Directorio 'data' no existe (se creará automáticamente)")
    else:
        print("  ✅ Directorio 'data' existe")
    
    return True

def check_imports():
    """Verifica que todos los módulos puedan importarse."""
    print("\n📦 Verificando imports...")
    
    # Cambiar al directorio del proyecto
    original_dir = os.getcwd()
    try:
        os.chdir(project_root)
        
        modules = [
            'app',
            'app.db',
            'app.models',
            'app.routes',
            'app.services',
            'app.utils'
        ]
        
        failed = []
        for module in modules:
            try:
                __import__(module)
                print(f"  ✅ {module}")
            except Exception as e:
                print(f"  ❌ {module}: {e}")
                failed.append(module)
        
        return len(failed) == 0
    finally:
        os.chdir(original_dir)

def main():
    """Ejecuta todas las verificaciones."""
    print("=" * 60)
    print("🔧 Verificación de Configuración - Gestiones MVP")
    print("=" * 60)
    
    checks = [
        ("Dependencias", check_dependencies),
        ("Imports", check_imports),
        ("Configuración", check_config),
        ("Base de Datos", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Error en verificación '{name}': {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Resumen:")
    print("=" * 60)
    
    all_ok = True
    for name, result in results:
        status = "✅ OK" if result else "❌ FALLO"
        print(f"  {status} - {name}")
        if not result:
            all_ok = False
    
    print("=" * 60)
    
    if all_ok:
        print("\n🎉 ¡Todo está configurado correctamente!")
        print("\nPróximos pasos:")
        print("  1. Ejecuta: python -m app.wsgi")
        print("  2. Abre: http://localhost:5000/gestiones")
        print("  3. Login con: admin / admin123")
        return 0
    else:
        print("\n⚠️  Hay problemas que resolver antes de continuar.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

