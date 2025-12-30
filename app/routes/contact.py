from flask import Blueprint, request, jsonify, current_app
import logging

from ..utils.validators import validate_email, sanitize_input
from ..utils.exceptions import ValidationError, EmailError, StorageError
from ..services.email_service import send_email_smtp
from ..services.storage import save_submission_to_file

logger = logging.getLogger(__name__)
bp = Blueprint("contact", __name__, url_prefix="/api")


@bp.route("/contact", methods=["POST"])
def contact():
    try:
        # Obtener y validar datos del formulario
        entity = request.form.get("entity", "").strip()
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        # Validar campos requeridos
        if not entity:
            raise ValidationError("El nombre de la entidad es requerido", field="entity")
        if not name:
            raise ValidationError("El nombre del contacto es requerido", field="name")
        if not email:
            raise ValidationError("El email es requerido", field="email")
        if not phone:
            raise ValidationError("El teléfono es requerido", field="phone")
        if not message:
            raise ValidationError("El mensaje es requerido", field="message")

        # Validar formato de email
        if not validate_email(email):
            raise ValidationError("Por favor ingrese un email válido", field="email")

        # Sanitizar entrada
        entity = sanitize_input(entity, 200)
        name = sanitize_input(name, 200)
        email = sanitize_input(email, 254)
        phone = sanitize_input(phone, 50)
        message = sanitize_input(message, 5000)

        logger.info(f"Nueva solicitud de contacto: {entity} - {name} ({email})")

        # Intentar enviar email
        email_sent = False
        subject = f"Nueva Solicitud de Propuesta - {entity}"
        body_text = _create_email_body_text(entity, name, email, phone, message)
        body_html = _create_email_body_html(entity, name, email, phone, message)

        if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
            try:
                recipients = current_app.config.get("CONTACT_RECIPIENTS", [])
                if not recipients:
                    logger.warning("CONTACT_RECIPIENTS no configurado, no se enviará email")
                else:
                    send_email_smtp(
                        recipients=recipients, subject=subject, body_text=body_text, body_html=body_html, reply_to=email
                    )
                    email_sent = True
                    logger.info(f"Email enviado exitosamente para solicitud de {entity}")
            except EmailError as e:
                # Log el error pero continuar (guardar la solicitud de todas formas)
                logger.error(f"Error al enviar email para solicitud de {entity}: {e}")
                # No re-lanzar, permitir que se guarde la solicitud

        # Guardar solicitud en archivo
        try:
            save_submission_to_file(entity, name, email, phone, message)
            logger.info(f"Solicitud guardada exitosamente: {entity}")
        except StorageError as e:
            logger.error(f"Error al guardar solicitud: {e}")
            # Si falla guardar, es crítico
            raise

        # Respuesta exitosa
        if email_sent:
            return jsonify(
                {
                    "success": True,
                    "message": "¡Gracias por su solicitud! Nuestro equipo se pondrá en contacto con usted para preparar una propuesta personalizada.",
                }
            )
        else:
            return jsonify(
                {
                    "success": True,
                    "message": "¡Gracias por su solicitud! Su solicitud ha sido registrada. Nuestro equipo se pondrá en contacto con usted pronto.",
                }
            )

    except (ValidationError, StorageError):
        # Re-lanzar excepciones de la app para que el error handler las maneje
        raise
    except Exception as e:
        logger.error(f"Error inesperado procesando solicitud de contacto: {e}", exc_info=True)
        raise


def _create_email_body_text(entity, name, email, phone, message):
    return f"""Nueva solicitud de propuesta recibida:

Entidad: {entity}
Contacto Responsable: {name}
Email: {email}
Teléfono: {phone}

Información de la cartera:
{message}

---
Este mensaje fue enviado desde el formulario de contacto del sitio web.
"""


def _create_email_body_html(entity, name, email, phone, message):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #7630b7;">Nueva Solicitud de Propuesta</h2>
        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Entidad:</strong> {entity}</p>
            <p><strong>Contacto Responsable:</strong> {name}</p>
            <p><strong>Email:</strong> <a href="mailto:{email}">{email}</a></p>
            <p><strong>Teléfono:</strong> {phone}</p>
        </div>
        <div style="background: #ffffff; padding: 20px; border-left: 4px solid #7630b7; margin: 20px 0;">
            <h3 style="color: #7630b7; margin-top: 0;">Información de la cartera:</h3>
            <p style="white-space: pre-wrap;">{message}</p>
        </div>
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="color: #888; font-size: 12px;">Este mensaje fue enviado desde el formulario de contacto del sitio web.</p>
    </body>
    </html>
    """
