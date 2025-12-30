"""
Utilidades de cache para optimización de performance.
"""
import json
import hashlib
from functools import wraps
from flask import current_app, request
from datetime import timedelta

try:
    import redis
    redis_available = True
except ImportError:
    redis_available = False


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Genera una clave de cache única basada en argumentos.
    
    Args:
        prefix: Prefijo para la clave
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
    
    Returns:
        Clave de cache
    """
    key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"cache:{prefix}:{key_hash}"


def get_redis_client():
    """Obtiene cliente Redis si está disponible."""
    if not redis_available:
        return None
    
    try:
        redis_url = current_app.config.get('REDIS_URL')
        if redis_url and redis_url.startswith('redis://'):
            return redis.from_url(redis_url, decode_responses=True)
        return None
    except Exception:
        return None


def cache_result(timeout: int = 300, key_prefix: str = None):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        timeout: Tiempo de expiración en segundos (default: 5 minutos)
        key_prefix: Prefijo para la clave de cache
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Intentar obtener de cache
            redis_client = get_redis_client()
            if redis_client:
                cache_key = get_cache_key(key_prefix or f.__name__, *args, **kwargs)
                cached = redis_client.get(cache_key)
                if cached:
                    try:
                        return json.loads(cached)
                    except:
                        pass
            
            # Ejecutar función
            result = f(*args, **kwargs)
            
            # Guardar en cache
            if redis_client:
                try:
                    redis_client.setex(
                        cache_key,
                        timeout,
                        json.dumps(result, default=str)
                    )
                except:
                    pass
            
            return result
        return decorated_function
    return decorator


def invalidate_cache(pattern: str):
    """
    Invalida entradas de cache que coincidan con un patrón.
    
    Args:
        pattern: Patrón de búsqueda (ej: 'cache:dashboard:*')
    """
    redis_client = get_redis_client()
    if redis_client:
        try:
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        except:
            pass

