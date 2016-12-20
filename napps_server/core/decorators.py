from flask import jsonify
from flask import request, Response
from jsonschema import validate
from jsonschema import ValidationError
from functools import wraps

from napps_server.core.models import User, Token
from napps_server.core.exceptions import NappsEntryDoesNotExists

def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if request.get_json() is None:
            return jsonify({'error': "Payload must be a valid json"}), 400
        return f(*args, **kw)
    return wrapper

def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                validate(request.json, schema)
            except ValidationError as e:
                return Response(e.message, 400)
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
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not User.check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return wrapper

def requires_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        content = request.get_json()
        try:
            token = Token.get(content['token'])
        except NappsEntryDoesNotExists:
            return Response("Permission denied", 401)
        except KeyError:
            return Response("Invalid request", 400)

        if not token.is_valid():
            return Response("Permission denied", 401)

        # Otherwise just send them where they wanted to go
        return f(token.user, *args, **kwargs)

    return wrapper
