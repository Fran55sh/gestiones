import json
import os
import tempfile
from datetime import datetime
from flask import current_app
import logging

from ..utils.validators import sanitize_input
from ..utils.exceptions import StorageError

logger = logging.getLogger(__name__)


def save_submission_to_file(entity, name, email, phone, message):
    """
    Guarda una solicitud de contacto en un archivo JSON.
    
    Args:
        entity: Nombre de la entidad
        name: Nombre del contacto
        email: Email del contacto
        phone: Teléfono del contacto
        message: Mensaje de la solicitud
    
    Returns:
        True si se guardó exitosamente
    
    Raises:
        StorageError: Si falla al guardar el archivo
    """
    submission = {
        'timestamp': datetime.now().isoformat(),
        'entity': sanitize_input(entity, 200),
        'name': sanitize_input(name, 200),
        'email': sanitize_input(email, 254),
        'phone': sanitize_input(phone, 50),
        'message': sanitize_input(message, 5000)
    }

    path = current_app.config.get('CONTACT_SUBMISSIONS_FILE')
    if not path:
        raise StorageError(
            "CONTACT_SUBMISSIONS_FILE no está configurado",
            operation='save',
            details={'config_missing': 'CONTACT_SUBMISSIONS_FILE'}
        )
    
    dir_path = os.path.dirname(path)
    
    try:
        # Crear directorio si no existe
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creando directorio {dir_path}: {e}")
        raise StorageError(
            f"No se pudo crear el directorio para guardar datos: {e}",
            operation='save',
            details={'directory': dir_path, 'os_error': str(e)}
        )

    try:
        # Leer archivo existente
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    submissions = json.load(f)
                if not isinstance(submissions, list):
                    logger.warning(f"Archivo {path} no contiene una lista, inicializando nueva lista")
                    submissions = []
            except json.JSONDecodeError as e:
                logger.warning(f"Error parseando JSON en {path}: {e}. Inicializando nueva lista")
                submissions = []
            except IOError as e:
                logger.error(f"Error leyendo archivo {path}: {e}")
                raise StorageError(
                    f"No se pudo leer el archivo de solicitudes: {e}",
                    operation='read',
                    details={'file': path, 'io_error': str(e)}
                )
        else:
            submissions = []

        # Agregar nueva solicitud
        submissions.append(submission)

        # Escribir de forma atómica usando archivo temporal
        try:
            with tempfile.NamedTemporaryFile('w', delete=False, dir=dir_path, encoding='utf-8') as tf:
                json.dump(submissions, tf, ensure_ascii=False, indent=2)
                temp_name = tf.name
            
            # Reemplazar archivo original de forma atómica
            os.replace(temp_name, path)
        except IOError as e:
            logger.error(f"Error escribiendo archivo {path}: {e}")
            # Intentar limpiar archivo temporal si existe
            if 'temp_name' in locals() and os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except Exception:
                    pass
            raise StorageError(
                f"No se pudo escribir el archivo de solicitudes: {e}",
                operation='write',
                details={'file': path, 'io_error': str(e)}
            )

        logger.info(f"Solicitud guardada exitosamente: {submission['entity']}")
        return True
        
    except StorageError:
        # Re-lanzar StorageError sin modificar
        raise
    except Exception as e:
        logger.error(f"Error inesperado guardando solicitud: {e}", exc_info=True)
        raise StorageError(
            f"Error inesperado al guardar solicitud: {e}",
            operation='save',
            details={'error': str(e), 'file': path}
        )
