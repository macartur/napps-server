# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

# Local source tree imports
from core.models import Token, Napp
from core.decorators import (validate_json, requires_token)
from core.exceptions import NappsEntryDoesNotExists

# Flask Blueprints
api = Blueprint('napp_api', __name__)

@api.route("/api/napps/", methods=["POST"])
@requires_token
@validate_json
def register_napp(user):
    """
    This endpoint will be used to register a new Network Application (napp).
    :return: Return HTTP code 201 if napp were succesfully created and 4XX in
    case of failure.
    """
    content = request.get_json()
    try:
        repository = content['repository']
    except KeyError:
        return Response("Invalid request", 400)

    if not user.enabled:
        return Response("Permission denied", 401)

    napp = Napp(repository)
    return Response("Napp created succesfully", 201)

#@api.route('/api/users/', methods=['GET'])
#def get_users():
#    """
#    This routine creates an endpoint that shows all applications developers
#    (application authors) with their information. It returns all information
#    in JSON format.
#    """
#
#    users = {user.username: user.as_dict() for user in User.all()}
#    return jsonify({'users': users }), 200
#
#@api.route('/api/users/<username>/', methods=['GET'])
#def get_user(username):
#    """
#    This routine creates an endpoint that shows details about a specific
#    application author. It returns all information in JSON format.
#    """
#    try:
#        user = User.get(username)
#    except NappsEntryDoesNotExists:
#        return jsonify({'error': 'User not found'}), 404
#
#    return jsonify(user.as_dict()), 200
