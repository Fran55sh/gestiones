from functools import wraps
from flask import session, redirect


def require_role(required_role: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print(f"Checking role {required_role} for session: {session}")
            if session.get('role') != required_role:
                print(f"Access denied. Expected {required_role}, got {session.get('role')}")
                return redirect('/gestiones')
            return f(*args, **kwargs)
        return decorated_function
    return decorator
