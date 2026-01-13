"""
Modelo de Caso/Deuda.
"""

from datetime import datetime, date
from ...core.database import db


class CaseStatus(db.Model):
    """Modelo de estado de caso."""

    __tablename__ = "case_statuses"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        """Convierte el estado a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<CaseStatus {self.id}: {self.nombre}>"


class Case(db.Model):
    """Modelo de caso de deuda."""

    __tablename__ = "cases"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)  # Nombre del deudor
    lastname = db.Column(db.String(200), nullable=False, index=True)  # Apellido del deudor
    dni = db.Column(db.String(50), nullable=True, index=True)
    nro_cliente = db.Column(db.String(100), nullable=True, index=True)  # Número de cliente
    total = db.Column(db.Numeric(15, 2), nullable=False)  # Monto total
    monto_inicial = db.Column(db.Numeric(15, 2), nullable=True)  # Monto inicial
    fecha_ultimo_pago = db.Column(db.Date, nullable=True)  # Fecha del último pago
    
    # Datos de contacto
    telefono = db.Column(db.String(50), nullable=True)
    
    # Datos de dirección
    calle_nombre = db.Column(db.String(200), nullable=True)
    calle_nro = db.Column(db.String(50), nullable=True)
    localidad = db.Column(db.String(200), nullable=True)
    cp = db.Column(db.String(20), nullable=True)  # Código postal
    provincia = db.Column(db.String(100), nullable=True)

    status_id = db.Column(db.Integer, db.ForeignKey("case_statuses.id"), nullable=False, default=1, index=True)
    cartera_id = db.Column(db.Integer, db.ForeignKey("carteras.id"), nullable=False, index=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    status_rel = db.relationship("CaseStatus", backref="cases", lazy="joined")
    cartera_rel = db.relationship("Cartera", backref="cases", lazy="joined")
    # assigned_gestor está definido como backref en User.cases
    promises = db.relationship("Promise", backref="case", lazy="dynamic", cascade="all, delete-orphan")
    activities = db.relationship("Activity", backref="case", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self, include_relations=False):
        """Convierte el caso a diccionario."""
        data = {
            "id": self.id,
            "name": self.name,
            "lastname": self.lastname,
            "dni": self.dni,
            "nro_cliente": self.nro_cliente,
            "total": float(self.total) if self.total else 0.0,
            "monto_inicial": float(self.monto_inicial) if self.monto_inicial else None,
            "fecha_ultimo_pago": self.fecha_ultimo_pago.isoformat() if self.fecha_ultimo_pago else None,
            "telefono": self.telefono,
            "calle_nombre": self.calle_nombre,
            "calle_nro": self.calle_nro,
            "localidad": self.localidad,
            "cp": self.cp,
            "provincia": self.provincia,
            "status_id": self.status_id,
            "status_nombre": self.status_rel.nombre if self.status_rel else None,
            "cartera_id": self.cartera_id,
            "cartera_nombre": self.cartera_rel.nombre if self.cartera_rel else None,
            "assigned_to_id": self.assigned_to_id,
            "assigned_to": self.assigned_gestor.username if hasattr(self, 'assigned_gestor') and self.assigned_gestor else None,
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
        return f"<Case {self.id}: {self.name} {self.lastname} - ${self.total}>"
