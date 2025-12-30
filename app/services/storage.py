import json
import os
import tempfile
from datetime import datetime
from flask import current_app
import logging

from ..db import db
from ..models import ContactSubmission
from ..utils.validators import sanitize_input
from ..utils.exceptions import StorageError

logger = logging.getLogger(__name__)


def save_submission_to_file(entity, name, email, phone, message):
    """
    Guarda una solicitud de contacto en la base de datos.
    
    Args:
        entity: Nombre de la entidad
        name: Nombre del contacto
        email: Email del contacto
        phone: Teléfono del contacto
        message: Mensaje de la solicitud
    
    Returns:
        True si se guardó exitosamente
    
    Raises:
        StorageError: Si falla al guardar
    """
    try:
        submission = ContactSubmission(
            entity=sanitize_input(entity, 200),
            name=sanitize_input(name, 200),
            email=sanitize_input(email, 254),
            phone=sanitize_input(phone, 50),
            message=sanitize_input(message, 5000)
        )
        
        db.session.add(submission)
        db.session.commit()
        
        logger.info(f"Solicitud guardada exitosamente en DB: {submission.entity}")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado guardando solicitud en DB: {e}", exc_info=True)
        raise StorageError(
            f"Error inesperado al guardar solicitud: {e}",
            operation='save',
            details={'error': str(e)}
        )
