from flask import Blueprint, jsonify, current_app
import logging

from ..core.database import db
from ..features.contact.models import ContactSubmission
from ..utils.security import require_role
from ..utils.exceptions import NotFoundError, StorageError

logger = logging.getLogger(__name__)
bp = Blueprint("admin", __name__, url_prefix="/api")


@bp.route("/submissions")
@require_role("admin")
def view_submissions():
    try:
        submissions = ContactSubmission.query.order_by(ContactSubmission.timestamp.desc()).all()

        logger.info(f"Leyendo {len(submissions)} solicitudes desde DB")
        return jsonify(
            {
                "success": True,
                "message": f"Total de solicitudes: {len(submissions)}",
                "submissions": [s.to_dict() for s in submissions],
            }
        )

    except Exception as e:
        logger.error(f"Error inesperado leyendo solicitudes: {e}", exc_info=True)
        raise StorageError(f"Error inesperado al leer solicitudes: {e}", operation="read")


@bp.route("/test-email-config")
@require_role("admin")
def test_email_config():
    cfg = current_app.config
    return jsonify(
        {
            "MAIL_SERVER": cfg.get("MAIL_SERVER"),
            "MAIL_PORT": cfg.get("MAIL_PORT"),
            "MAIL_USE_TLS": cfg.get("MAIL_USE_TLS"),
            "MAIL_USE_SSL": cfg.get("MAIL_USE_SSL"),
            "MAIL_USERNAME": cfg.get("MAIL_USERNAME"),
            "MAIL_PASSWORD": "Configurado" if cfg.get("MAIL_PASSWORD") else "No configurado",
            "MAIL_DEFAULT_SENDER": cfg.get("MAIL_DEFAULT_SENDER"),
            "has_credentials": bool(cfg.get("MAIL_USERNAME") and cfg.get("MAIL_PASSWORD")),
        }
    )
