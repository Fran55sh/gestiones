"""
Modelo de Promesa de Pago.
"""
from datetime import datetime
from ..core.database import db


class Promise(db.Model):
    """Modelo de promesa de pago."""
    __tablename__ = 'promises'
    
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    promise_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, default='pending', index=True)
    # Estados: pending, fulfilled, broken
    
    fulfilled_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convierte la promesa a diccionario."""
        return {
            'id': self.id,
            'case_id': self.case_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'promise_date': self.promise_date.isoformat() if self.promise_date else None,
            'status': self.status,
            'fulfilled_date': self.fulfilled_date.isoformat() if self.fulfilled_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f'<Promise {self.id}: ${self.amount} - {self.promise_date}>'

