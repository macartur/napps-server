# System imports

# Third-party imports
from flask import Blueprint
from flask import request
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


@api.route("/api/confirm/<token>", methods=["GET"])
def confirm_auth(token):
    """
    Endpoint to change an inactive user to active
    :param token: A token of type "Validation"
    :return: Code 200 if activation was successfully or an Error (4xx) code otherwise
    """

    stored_token = con.hgetall(token)
    register_token = common.Token(token_exp_time=stored_token["expire"],
                                  token_id=token,
                                  token_gen_time=stored_token["creation"],
                                  token_type=stored_token["type"]
                                  )
    register_user = common.User(login=register_token.token_to_login())
    if register_token.token_type == "Validation" and register_user.is_active is False:
        author_key = "author:"+ register_user.login
        con.hset(author_key, "status", "active")
        return '', 200
    else:
        return '', 401
