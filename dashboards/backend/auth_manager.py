import jwt
import datetime
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "darkwin_secret_key_change_me"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid"}), 401
        return f(*args, **kwargs)
    return decorated

def generate_token(username):
    token = jwt.encode({
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY)
    return token
