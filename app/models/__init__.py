"""
Modelos de base de datos para Gestiones MVP.
Re-exporta modelos desde app.features para mantener compatibilidad.
"""

from app.features.users.models import User
from app.features.cases.models import Case
from app.features.cases.promise import Promise
from app.features.activities.models import Activity
from app.features.contact.models import ContactSubmission

__all__ = ["User", "Case", "Promise", "Activity", "ContactSubmission"]
