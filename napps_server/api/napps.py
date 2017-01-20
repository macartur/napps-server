"""Module used to make avaliable napps routes."""
# System imports

# Third-party imports
from flask import Blueprint, Response, jsonify, request

from napps_server.core.decorators import requires_token, validate_json
from napps_server.core.exceptions import (InvalidAuthor, InvalidNappMetaData,
                                          NappsEntryDoesNotExists)
# Local source tree imports
from napps_server.core.models import Napp, User

# Flask Blueprints
api = Blueprint('napp_api', __name__)


@api.route('/napps/', methods=['GET'])
def get_napps():
    """Method used to shows all network applications.

    This method creates the '/napps/' endpoint to show all network applications
    as a json format.

    Returns:
        json (string): Strnig with all information in JSON format.
    """
    napps = [napp.as_dict() for napp in Napp.all()]
    params = request.args
    length = params.get('length')
    if length and int(length) > 0:
        napps = napps[0:int(length)]
    return jsonify({'napps': napps}), 200


@api.route('/napps/<author>/', methods=['GET'])
@api.route('/napps/<author>/<name>/', methods=['GET'])
def get_napp(author, name=''):
    """Method used to show a detailed napp information.

    This method creates the '/napps/<author>/<name>' endpoint that shows a
    detailed napp information as a json format.

    Parameters:
        author (string): Author name.
        name (string): Napp name.
    Returns
        json (string): String with all information in JSON format.
    """
    try:
        user = User.get(author)
    except NappsEntryDoesNotExists:
        return jsonify({
            'error': 'Author {} not found'.format(author)
        }), 404

    if not name:
        napps = [napp.as_dict() for napp in user.get_all_napps()]
        return jsonify(napps), 200

    try:
        napp = user.get_napp_by_name(name)
    except NappsEntryDoesNotExists:
        return jsonify({
            'error': 'NApp {} not found for the author {}'.format(name, author)
        }), 404

    return jsonify(napp.as_dict()), 200


@api.route("/napps/", methods=["POST"])
@requires_token
@validate_json
def register_napp(user):
    """Method to register a new Network Application.

    This method creates the '/napps' endpoint to register a new Network
    Application.

    :return: Return HTTP code 201 if napp were succesfully created and 4XX in
    case of failure.
    """
    content = request.get_json()
    if not user.enabled or not content['author'] == user.username:
        return Response("Permission denied", 401)

    try:
        Napp.new_napp_from_dict(content, user)
    except InvalidAuthor:
        return Response("Permission denied. Invalid Author.", 401)
    except InvalidNappMetaData:
        return Response("Permission denied. Invalid metadata.", 401)

    return Response("Napp created succesfully", 201)
