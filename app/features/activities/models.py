"""
Modelo de Actividad/Gestión.
"""

from datetime import datetime
from ...core.database import db


class Activity(db.Model):
    """Modelo de actividad de gestión."""

    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    # Tipos: call, email, visit, note, payment, promise

    notes = db.Column(db.Text, nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    def to_dict(self):
        """Convierte la actividad a diccionario."""
        return {
            "id": self.id,
            "case_id": self.case_id,
            "type": self.type,
            "notes": self.notes,
            "created_by_id": self.created_by_id,
            "created_by": self.creator.username if self.creator else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Activity {self.id}: {self.type} on case {self.case_id}>"
