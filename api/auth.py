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
    :return: A token to the user and the expiration time (epoch)
    """
    content = request.get_json(silent=True)

    try:
        validate(content, common.napps_auth)
        user = content['login']
        password = common.hash_pass(content['password'])
        current_user = common.Users(login=user)

        if password == current_user.hash_pass:
            user_new_token = common.Tokens.token_gen(current_user.login)
            return jsonify(user_new_token), 200
        else:
            return '', 401

    except ValidationError:
        return '', 400
