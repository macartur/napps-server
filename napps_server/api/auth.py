# System imports

# Third-party imports
from flask import Blueprint, jsonify, request

# Local source tree imports
from napps_server.core.decorators import requires_auth
from napps_server.core.exceptions import NappsEntryDoesNotExists
from napps_server.core.models import User

# Flask Blueprints
api = Blueprint('auth_api', __name__)

@api.route("/auth/", methods=["POST"])
@requires_auth
def napps_auth():
    """
    Endpoint to perform the authentication
    :return: A token to the user
    """
    try:
        auth = request.authorization
        user = User.get(auth.username)
    except NappsEntryDoesNotExists:
        return jsonify({'error': 'User not found'}), 404

    token = user.create_token()
    return jsonify(token.as_dict()), 201
