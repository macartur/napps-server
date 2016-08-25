from flask import jsonify
from flask import request
from jsonschema import validate
from jsonschema import ValidationError
from functools import wraps

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

