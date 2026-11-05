from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request

from app.models import Role


def roles_required(*roles: Role) -> Callable:
    allowed = {role.value for role in roles}

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            verify_jwt_in_request()
            if get_jwt().get("role") not in allowed:
                return jsonify(error="You do not have permission to perform this action"), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
