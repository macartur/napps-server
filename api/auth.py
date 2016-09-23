# System imports

# Third-party imports
from flask import Blueprint
from flask import request
from flask import jsonify

# Local source tree imports
from core.decorators import requires_auth
from core.exceptions import NappsEntryDoesNotExists
from core.models import User

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
        user = User.get(request.authorization.username)
    except NappsEntryDoesNotExists:
        return jsonify({'error': 'User not found'}), 404

    token = user.create_token()
    return jsonify(token.as_dict()), 201
