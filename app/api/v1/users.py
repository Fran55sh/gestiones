"""
Endpoints API para usuarios (admin).
"""

from flask import jsonify

from ...features.users.models import User
from ...utils.security import require_role

from . import bp


@bp.route("/users/gestores")
@require_role("admin")
def list_gestores():
    """Lista gestores activos para asignación de casos (solo admin)."""
    try:
        gestores = (
            User.query.filter(User.role == "gestor", User.active.is_(True))
            .order_by(User.username)
            .all()
        )
        return jsonify(
            {
                "success": True,
                "data": [{"id": g.id, "username": g.username} for g in gestores],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
