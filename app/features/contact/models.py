"""
Modelo de Solicitud de Contacto.
"""
from datetime import datetime
from ...core.database import db


class ContactSubmission(db.Model):
    """Modelo de solicitud de contacto desde el formulario."""
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    entity = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(254), nullable=False, index=True)
    phone = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convierte la solicitud a diccionario."""
        return {
            'id': self.id,
            'entity': self.entity,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }
    
    def __repr__(self):
        return f'<ContactSubmission {self.id}: {self.entity} - {self.email}>'

