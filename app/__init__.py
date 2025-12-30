"""
Application factory for Gestiones MVP (Flask).
"""
import os
import json
import logging
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify, request
from flask_compress import Compress
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import HTTPException

from .core.database import db
from .features.users.models import User
from .features.cases.models import Case
from .features.cases.promise import Promise
from .features.activities.models import Activity
from .features.contact.models import ContactSubmission

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "on", "yes")


def _env_list(name: str, default_list):
    raw = os.environ.get(name)
    if not raw:
        return default_list
    return [item.strip() for item in raw.split(",") if item.strip()]


def create_app() -> Flask:
    # Paths
    package_dir = Path(__file__).parent
    project_root = package_dir.parent.resolve()
    static_dir = project_root / "static"

    # App
    app = Flask(
        __name__,
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    # Core config
    app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production-" + os.urandom(32).hex())
    app.config["SESSION_COOKIE_SECURE"] = _env_bool("SESSION_COOKIE_SECURE", False)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=int(os.environ.get("SESSION_LIFETIME_HOURS", "8")))
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = int(os.environ.get("SEND_FILE_MAX_AGE_DEFAULT", "3600"))

    # Proxy headers (for Nginx/LB)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)  # type: ignore

    # Mail config
    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.zoho.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 465))
    app.config["MAIL_USE_TLS"] = _env_bool("MAIL_USE_TLS", False)
    app.config["MAIL_USE_SSL"] = _env_bool("MAIL_USE_SSL", True)
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])
    app.config["MAIL_TIMEOUT"] = 20

    # Database config
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        # Default to SQLite in data directory
        data_dir = project_root / "data"
        data_dir.mkdir(exist_ok=True)
        database_url = f"sqlite:///{data_dir / 'gestiones.db'}"
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = _env_bool("SQLALCHEMY_ECHO", False)
    
    # Initialize database
    db.init_app(app)
    
    # Compression
    Compress(app)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        # Migrate default users if they don't exist
        _migrate_default_users(app)

    # Project paths in config
    app.config["ROOT_DIR"] = str(project_root)
    app.config["ALLOWED_STATIC_EXTENSIONS"] = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".css", ".js"}

    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    app.config["CONTACT_SUBMISSIONS_FILE"] = str(data_dir / "contact_submissions.json")

    # Recipients (env override supported)
    app.config["CONTACT_RECIPIENTS"] = _env_list(
        "CONTACT_RECIPIENTS",
        [
            "emanuel.cariman@novagestiones.com.ar",
            "victor.laumann@novagestiones.com.ar",
            "angeles.laumann@novagestiones.com.ar",
        ],
    )

    # Legacy support: mantener app.config["USERS"] para compatibilidad temporal
    # Esto será removido una vez que auth.py esté completamente migrado
    app.config["USERS"] = {}

    # CSRF - Habilitado por defecto en producción
    enable_csrf = _env_bool("ENABLE_CSRF", not app.debug)
    if enable_csrf:
        try:
            from flask_seasurf import SeaSurf
            SeaSurf(app)
            logger.info("CSRF habilitado con Flask-SeaSurf")
        except Exception as e:
            logger.warning(f"ENABLE_CSRF activo pero Flask-SeaSurf no disponible: {e}")
    
    # Rate Limiting
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=os.environ.get("REDIS_URL", "memory://")
        )
        app.config["RATELIMIT_ENABLED"] = True
        logger.info("Rate limiting habilitado")
    except Exception as e:
        logger.warning(f"Rate limiting no disponible: {e}")

    # Blueprints - Web routes (HTML)
    from .web.auth import bp as auth_bp
    from .web.dashboards import bp as dashboards_bp
    from .web.contact import bp as contact_bp
    from .web.admin import bp as admin_bp
    from .web.public import bp as root_bp
    
    # Blueprints - API routes (REST)
    from .api.v1 import bp as api_v1_bp

    # Register web blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(root_bp)
    
    # Register API blueprints
    app.register_blueprint(api_v1_bp)

    # Health
    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"})

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://unpkg.com https://*.unpkg.com https://cdn.tailwindcss.com; connect-src 'self' https://unpkg.com https://*.unpkg.com",
        )
        return response

    # Error handlers centralizados
    from .utils.error_handler import handle_app_error, handle_http_exception, handle_generic_exception
    from .utils.exceptions import AppError
    
    @app.errorhandler(AppError)
    def handle_app_error_wrapper(error):
        return handle_app_error(error)
    
    @app.errorhandler(404)
    @app.errorhandler(403)
    @app.errorhandler(401)
    @app.errorhandler(400)
    def handle_http_errors(error):
        return handle_http_exception(error)
    
    @app.errorhandler(500)
    def handle_500(error):
        return handle_generic_exception(error)
    
    @app.errorhandler(Exception)
    def handle_all_exceptions(error):
        # Si ya es un AppError o HTTPException, dejar que otros handlers lo manejen
        if isinstance(error, (AppError, HTTPException)):
            raise error
        return handle_generic_exception(error)

    return app


def _migrate_default_users(app):
    """Migra usuarios por defecto a la base de datos si no existen."""
    default_users = {
        "admin": {"password": "admin123", "role": "admin"},
        "gestor": {"password": "gestor123", "role": "gestor"},
        "usuario": {"password": "user123", "role": "user"},
    }
    
    for username, user_data in default_users.items():
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(
                username=username,
                role=user_data["role"],
                active=True
            )
            new_user.set_password(user_data["password"])
            db.session.add(new_user)
            logger.info(f"Usuario por defecto creado: {username} ({user_data['role']})")
    
    db.session.commit()


