"""
Modelo de Caso/Deuda.
"""

from datetime import datetime
from ...core.database import db


class Case(db.Model):
    """Modelo de caso de deuda."""

    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(200), nullable=False, index=True)  # Entidad que debe
    debtor_name = db.Column(db.String(200), nullable=False, index=True)
    dni = db.Column(db.String(50), nullable=True, index=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="en_gestion", index=True)
    # Estados: en_gestion, promesa, pagada, incobrable

    # Estado detallado de gestión para el frontend
    management_status = db.Column(db.String(50), nullable=True, default="sin-gestion", index=True)
    # Estados: sin-gestion, contactado, con-arreglo, incobrable, de-baja

    cartera = db.Column(db.String(100), nullable=False, index=True)  # Cartera A, B, C, etc.
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    promises = db.relationship("Promise", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="case", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_relations=False):
        """Convierte el caso a diccionario."""
        data = {
            "id": self.id,
            "entity": self.entity,
            "debtor_name": self.debtor_name,
            "dni": self.dni,
            "amount": float(self.amount) if self.amount else 0.0,
            "status": self.status,
            "management_status": self.management_status or "sin-gestion",
            "cartera": self.cartera,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to": self.assigned_gestor.username if self.assigned_gestor else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relations:
            from ..activities.models import Activity

            data["promises"] = [p.to_dict() for p in self.promises.all()]
            data["activities"] = [a.to_dict() for a in self.activities.order_by(Activity.created_at.desc()).limit(10).all()]

        return data

    def __repr__(self):
        return f"<Case {self.id}: {self.debtor_name} - ${self.amount}>"
