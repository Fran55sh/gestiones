import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from flask import current_app
import logging

from ..utils.exceptions import EmailError, ConfigurationError

logger = logging.getLogger(__name__)


def send_email_smtp(recipients, subject, body_text, body_html, from_email=None, reply_to=None):
    """
    Envía un email usando SMTP.

    Args:
        recipients: Lista de destinatarios
        subject: Asunto del email
        body_text: Cuerpo del email en texto plano
        body_html: Cuerpo del email en HTML
        from_email: Email del remitente (opcional)
        reply_to: Email para Reply-To (opcional)

    Returns:
        True si se envió exitosamente, False si no hay credenciales configuradas

    Raises:
        ConfigurationError: Si falta configuración crítica
        EmailError: Si falla el envío del email
    """
    cfg = current_app.config

    # Validar configuración
    if not cfg.get("MAIL_USERNAME") or not cfg.get("MAIL_PASSWORD"):
        logger.warning("Credenciales de email no configuradas")
        return False

    if not cfg.get("MAIL_SERVER"):
        raise ConfigurationError("MAIL_SERVER no está configurado", config_key="MAIL_SERVER")

    if not recipients:
        raise EmailError("No se especificaron destinatarios")

    from_email = from_email or cfg["MAIL_USERNAME"]
    server = None

    try:
        # Construir mensaje
        email_msg = MIMEMultipart("alternative")
        email_msg["Subject"] = subject
        email_msg["From"] = formataddr(("NOVA Gestión de Cobranzas", from_email))
        email_msg["To"] = ", ".join(recipients)
        if reply_to:
            email_msg["Reply-To"] = reply_to

        text_part = MIMEText(body_text, "plain", "utf-8")
        html_part = MIMEText(body_html, "html", "utf-8")
        email_msg.attach(text_part)
        email_msg.attach(html_part)

        # Conectar al servidor SMTP
        mail_server = cfg["MAIL_SERVER"]
        mail_port = cfg["MAIL_PORT"]
        mail_timeout = cfg.get("MAIL_TIMEOUT", 20)

        if cfg.get("MAIL_USE_SSL"):
            logger.info(f"Conectando con SSL a {mail_server}:{mail_port}")
            server = smtplib.SMTP_SSL(mail_server, mail_port, timeout=mail_timeout)
        else:
            logger.info(f"Conectando con TLS a {mail_server}:{mail_port}")
            server = smtplib.SMTP(mail_server, mail_port, timeout=mail_timeout)
            if cfg.get("MAIL_USE_TLS"):
                server.starttls()

        # Autenticar
        logger.info("Autenticando en servidor SMTP")
        server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])

        # Enviar
        logger.info(f"Enviando email a {len(recipients)} destinatarios")
        server.send_message(email_msg, from_addr=from_email, to_addrs=recipients)

        logger.info("Email enviado exitosamente")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Error de autenticación SMTP: {e}")
        raise EmailError("Error de autenticación con el servidor de email", details={"smtp_error": str(e)})
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP: {e}")
        raise EmailError("Error al enviar email", details={"smtp_error": str(e), "server": mail_server, "port": mail_port})
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error(f"Error de conexión al servidor SMTP: {e}")
        raise EmailError(
            "No se pudo conectar al servidor de email",
            details={"connection_error": str(e), "server": mail_server, "port": mail_port},
        )
    except Exception as e:
        logger.error(f"Error inesperado al enviar email: {e}", exc_info=True)
        raise EmailError("Error inesperado al enviar email", details={"error": str(e)})
    finally:
        if server:
            try:
                server.quit()
            except Exception as e:
                logger.debug(f"Error al cerrar conexión SMTP: {e}")
