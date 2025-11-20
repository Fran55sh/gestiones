from flask import Blueprint, jsonify, current_app
import json
import logging
from pathlib import Path

from ..utils.security import require_role
from ..utils.exceptions import NotFoundError, StorageError

logger = logging.getLogger(__name__)
bp = Blueprint('admin', __name__, url_prefix='/api')


@bp.route('/submissions')
@require_role('admin')
def view_submissions():
    try:
        file_path = current_app.config.get('CONTACT_SUBMISSIONS_FILE')
        if not file_path:
            raise StorageError(
                "CONTACT_SUBMISSIONS_FILE no está configurado",
                operation='read'
            )
        
        path = Path(file_path)
        
        if not path.exists():
            logger.info("Archivo de solicitudes no existe, retornando lista vacía")
            return jsonify({
                'success': True,
                'message': 'No hay solicitudes guardadas aún.',
                'submissions': []
            })
        
        try:
            with path.open('r', encoding='utf-8') as f:
                submissions = json.load(f)
            
            if not isinstance(submissions, list):
                logger.warning(f"Archivo {path} no contiene una lista válida")
                submissions = []
            
            logger.info(f"Leyendo {len(submissions)} solicitudes")
            return jsonify({
                'success': True,
                'message': f'Total de solicitudes: {len(submissions)}',
                'submissions': submissions
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON en {path}: {e}")
            raise StorageError(
                f"El archivo de solicitudes está corrupto: {e}",
                operation='read',
                details={'file': str(path), 'json_error': str(e)}
            )
        except IOError as e:
            logger.error(f"Error leyendo archivo {path}: {e}")
            raise StorageError(
                f"No se pudo leer el archivo de solicitudes: {e}",
                operation='read',
                details={'file': str(path), 'io_error': str(e)}
            )
            
    except StorageError:
        # Re-lanzar StorageError
        raise
    except Exception as e:
        logger.error(f"Error inesperado leyendo solicitudes: {e}", exc_info=True)
        raise StorageError(
            f"Error inesperado al leer solicitudes: {e}",
            operation='read'
        )


@bp.route('/test-email-config')
@require_role('admin')
def test_email_config():
    cfg = current_app.config
    return jsonify({
        'MAIL_SERVER': cfg.get('MAIL_SERVER'),
        'MAIL_PORT': cfg.get('MAIL_PORT'),
        'MAIL_USE_TLS': cfg.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': cfg.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': cfg.get('MAIL_USERNAME'),
        'MAIL_PASSWORD': 'Configurado' if cfg.get('MAIL_PASSWORD') else 'No configurado',
        'MAIL_DEFAULT_SENDER': cfg.get('MAIL_DEFAULT_SENDER'),
        'has_credentials': bool(cfg.get('MAIL_USERNAME') and cfg.get('MAIL_PASSWORD'))
    })

