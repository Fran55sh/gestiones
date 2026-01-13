"""
Modelo de Cartera/Empresa.
"""

from datetime import datetime
from ...core.database import db


class Cartera(db.Model):
    """Modelo de cartera/empresa."""

    __tablename__ = "carteras"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), unique=True, nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convierte la cartera a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Cartera {self.id}: {self.nombre}>"

