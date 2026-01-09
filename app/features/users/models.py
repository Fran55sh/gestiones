"""
Modelo de Usuario.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ...core.database import db


class User(db.Model):
    """Modelo de usuario del sistema."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)  # admin, gestor, user
    active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    cases = db.relationship("Case", backref="assigned_gestor", lazy="dynamic", foreign_keys="Case.assigned_to_id")
    activities = db.relationship("Activity", backref="creator", lazy="dynamic")

    def set_password(self, password: str):
        """Establece la contraseña hasheada."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convierte el usuario a diccionario (sin contraseña)."""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
