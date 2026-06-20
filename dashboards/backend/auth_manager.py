"""DARKWIN Dashboard Authentication Manager.

Handles JWT token generation and validation for the DARKWIN web dashboard API.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
import datetime
from functools import wraps

import jwt
from flask import request, jsonify

SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "darkwin_secret_key_change_me")


def token_required(f):
    """Decorator that enforces JWT token authentication on a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
            return jsonify({"message": "Token is invalid"}), 401
        return f(*args, **kwargs)
    return decorated


def generate_token(username: str) -> str:
    """Generate a JWT token for a given username.

    Args:
        username: User identifier for the token.

    Returns:
        Encoded JWT token string valid for 24 hours.
    """
    payload = {
        "user": username,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY)
