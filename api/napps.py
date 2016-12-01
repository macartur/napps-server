# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

# Local source tree imports
from core.models import Token, Napp, User
from core.decorators import (validate_json, requires_token)
from core.exceptions import NappsEntryDoesNotExists
from core.exceptions import InvalidAuthor
from core.exceptions import InvalidNappMetaData

# Flask Blueprints
api = Blueprint('napp_api', __name__)


@api.route('/napps/', methods=['GET'])
def get_napps():
    """
    This routine creates an endpoint that shows all network applications.
    It returns all information in JSON format.
    """
    napps = [napp.as_dict() for napp in Napp.all()]
    return jsonify({'napps': napps }), 200


@api.route('/napps/<author>/<name>/', methods=['GET'])
def get_napp(author, name):
    """
    This routine creates an endpoint that shows a detailed napp information.
    It returns all information in JSON format.
    """
    try:
        user = User.get(author)
    except NappsEntryDoesNotExists:
        return jsonify({'error': 'Napp not found'}), 404

    napp = user.get_napp_by_name(name)
    if napp is None:
        return jsonify({'error': 'Napp not found'}), 404

    return jsonify(napp.as_dict()), 200


@api.route("/napps/", methods=["POST"])
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
        git = content['git']
    except KeyError:
        return Response("Invalid request", 400)

    if not user.enabled:
        return Response("Permission denied", 401)

    try:
      napp = Napp(git, user)
    except InvalidAuthor:
        return Response("Permission denied. Invalid Author.", 401)
    except InvalidNappMetaData:
        return Response("Permission denied. Invalid metadata.", 401)

    return Response("Napp created succesfully", 201)
