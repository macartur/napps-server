# System imports

# Third-party imports
from flask import Blueprint
from flask import request
from flask import jsonify
from jsonschema import validate
from jsonschema import ValidationError

# Local source tree imports
import config
from api import common

con = config.CON


# Flask Blueprints
api = Blueprint('auth_api', __name__)


@api.route("/api/auth/", methods=["POST"])
def napps_auth():
    """
    Endpoint to perform the authentication
    :return: A token to the user
    """
    content = request.get_json(silent=True)

    try:
        validate(content, common.napps_auth)
        user = content['login']
        password = common.hash_pass(content['password'])
        current_user = common.User(login=user)

        if password == current_user.hash_pass and current_user.is_active:
            user_new_token = common.token_gen("Auth")
            user_new_token.token_store(user)
            return user_new_token.token_id, 200
        else:
            return '', 401
    except ValidationError:
        return '', 400
