"""Module with main decoretors used by napps-server."""
from functools import wraps

from flask import Response, jsonify, request
from jsonschema import ValidationError, validate

from napps_server.core.exceptions import NappsEntryDoesNotExists
from napps_server.core.models import Token, User


def validate_json(f):
    """Method used to validate a json from request."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper called to validate a json from request."""
        if request.get_json() is None:
            return jsonify({'error': "Payload must be a valid json"}), 400
        return f(*args, **kwargs)
    return wrapper


def validate_schema(schema):
    """Method used to validate a json from request using a schema."""
    def decorator(f):
        """Decorator to be called when validate_schema is called."""
        @wraps(f)
        def wrapper(*args, **kwargs):
            """Wrapper to validate the schema."""
            try:
                validate(request.get_json(), schema)
            except ValidationError as e:
                return Response(e.message, 400)
            return f(*args, **kwargs)
        return wrapper
    return decorator


def authenticate():
    """Method used to send a 401 response that enables basic auth."""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    """Method used to handle user authentication."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper to verify the user authentication."""
        auth = request.authorization
        if not auth or not User.check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return wrapper


def requires_token(f):
    """Method used to handle tokens from requests."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        """Wrapper used to verify the requires of token."""
        content = request.get_json()
        try:
            token = Token.get(content['token'])
        except NappsEntryDoesNotExists:
            return Response("Permission denied", 401)
        except KeyError:
            return Response("Invalid request", 400)
        except TypeError:
            return Response("Invalid request", 400)

        if not token.is_valid():
            return Response("Permission denied", 401)

        # Otherwise just send them where they wanted to go
        return f(token.user, *args, **kwargs)

    return wrapper
