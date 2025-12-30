import logging
from functools import wraps
from flask import session, redirect

logger = logging.getLogger(__name__)


def require_role(required_role: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = session.get('role')
            if user_role != required_role:
                logger.warning(f"Access denied. User role: {user_role}, required: {required_role}")
                return redirect('/gestiones')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
