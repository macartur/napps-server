from flask import jsonify
from flask import request, Response
from jsonschema import validate
from jsonschema import ValidationError
from functools import wraps

from core.models import User

def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
#        try:
        request.json
#        except BadRequest as e:
#            msg = "Payload must be a valid json"
#            return jsonify({"error": msg}), 400
        return f(*args, **kw)
    return wrapper


def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                validate(request.json, schema)
            except ValidationError as e:
                return jsonify({"error": e.message}), 400
            return f(*args, **kw)
        return wrapper
    return decorator

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not User.check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
