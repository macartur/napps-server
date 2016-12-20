# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request
from flask import Response

# Local source tree imports
from napps_server.core.models import Token, Napp, User
from napps_server.core.decorators import (validate_json, requires_token)
from napps_server.core.exceptions import NappsEntryDoesNotExists
from napps_server.core.exceptions import InvalidAuthor
from napps_server.core.exceptions import InvalidNappMetaData

# Flask Blueprints
api = Blueprint('napp_api', __name__)


@api.route('/napps/', methods=['GET'])
def get_napps():
    """
    This routine creates an endpoint that shows all network applications.
    It returns all information in JSON format.
    """
    napps = [napp.as_dict() for napp in Napp.all()]
    params = request.args
    length = params.get('length')
    if length and int(length) > 0:
        napps = napps[0:int(length)]
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
        return jsonify({
            'error': 'Author {} not found'.format(author)
        }), 404

    napp = user.get_napp_by_name(name)
    if napp is None:
        return jsonify({
            'error': 'NApp {} not found for the author {}'.format(name, author)
        }), 404

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
    if not user.enabled or not content['author'] == user.username :
        return Response("Permission denied", 401)

    try:
        napp = Napp.new_napp_from_dict(content, user)
    except InvalidAuthor:
        return Response("Permission denied. Invalid Author.", 401)
    except InvalidNappMetaData:
        return Response("Permission denied. Invalid metadata.", 401)

    return Response("Napp created succesfully", 201)
