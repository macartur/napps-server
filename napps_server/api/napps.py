"""Module used to make avaliable napps routes."""
# System imports
import os
import re
from time import strftime

# Third-party imports

# Local source tree imports
from flask import Blueprint, Response, jsonify, request

from napps_server.core.decorators import requires_token, validate_json
from napps_server.core.exceptions import (InvalidUser, InvalidNappMetaData,
                                          NappsEntryDoesNotExists)
from napps_server.core.models import Napp, User
from napps_server.core.utils import get_request_data

# Flask Blueprints
api = Blueprint('napp_api', __name__)

NAPP_REPO = '/var/www/kytos/napps/repo'
ALLOWED_EXTENSIONS = set(['napp'])


def _allowed_file(filename):
    """Check if the filename matches one of the required extensions."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def _curr_date():
    """Return current date on the format YYYMMDDD."""
    return strftime("%Y%m%d")


def _napp_versioned_name(username, napp_name):
    """Build the napp filename with a timestamp and a counter."""
    user_repo = os.path.join(NAPP_REPO, username)
    basename = napp_name + '-' + _curr_date() + '-'
    regexp = re.compile(r'' + basename + '(\d+)' + '.napp')
    counter = 0
    for file in os.listdir(user_repo):
        matched = regexp.match(file)
        if matched and int(matched.group(1)) > counter:
            counter = int(matched.group(1))
    return basename + str(counter + 1) + '.napp'


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


@api.route('/napps/<username>/', methods=['GET'])
@api.route('/napps/<username>/<name>/', methods=['GET'])
def get_napp(username, name=''):
    """Method used to show a detailed napp information.

    This method creates the '/napps/<username>/<name>' endpoint that shows
    a detailed napp information as a json format.

    Parameters:
        username (string): Name of a user.
        name (string): Napp name.

    Returns:
        json (string): String with all information in JSON format.
        HTTP code 404 if no user was found with the given username.
        HTTP code 404 if the NApp was not found for the given user.
    """
    try:
        user = User.get(username)
    except NappsEntryDoesNotExists:
        return jsonify({
            'error': 'Username {} not found'.format(username)
        }), 404

    if not name:
        napps = [napp.as_dict() for napp in user.get_all_napps()]
        return jsonify(napps), 200

    try:
        napp = user.get_napp_by_name(name)
    except NappsEntryDoesNotExists:
        return jsonify({
            'error': 'NApp {} not found for the username {}'.format(name,
                                                                    username)
        }), 404

    return jsonify(napp.as_dict()), 200


@api.route("/napps/", methods=["POST"])
@requires_token
@validate_json
def register_napp(user):
    """Method to register a new Network Application.

    This method creates the '/napps' endpoint to register a new Network
    Application.

    Returns:
        HTTP code 201 if napp were succesfully created.
        HTTP code 400 if there were not .napp file sent on the request.
        HTTP code 400 if there were errors on the NApp metadata.
        HTTP code 401 if the current user is trying to upload someone else NApp
    """
    #: As we expect here a multipart/form POST, then the 'data' may come on the
    #: form attribute of the request, instead of the json attribute.
    content = get_request_data(request, Napp.schema)

    # Get the name of the uploaded file
    sent_file = request.files.get('file')

    username = content.get('username')
    napp_name = content.get('name')

    if not sent_file or not _allowed_file(sent_file.filename):
        return Response("Invalid file/file extension.", 400)

    try:
        Napp.new_napp_from_dict(content, user)
    except InvalidUser:
        return Response("Permission denied.", 401)
    except InvalidNappMetaData:
        return Response("Invalid metadata.", 400)

    user_repo = os.path.join(NAPP_REPO, username)
    os.makedirs(user_repo, exist_ok=True)
    napp_latest = napp_name + '-latest.napp'
    napp_filename = _napp_versioned_name(username, napp_name)
    # Move the file form the temporal folder to
    # the upload folder we setup
    sent_file.save(os.path.join(user_repo, napp_filename))

    # Updating the 'latest' version, symbolic linking it to the uploaded file.
    try:
        os.remove(os.path.join(user_repo, napp_latest))
    except FileNotFoundError:
        pass
    os.symlink(os.path.join(user_repo, napp_filename),
               os.path.join(user_repo, napp_latest))

    return Response("Napp succesfully created", 201)


# @api.route('/napps/<username>/<name>/', methods=['DELETE'])
@requires_token
def delete_napp(user, username, name):
    """Method used to delete a NApp.

    This method receives a "DELETE" HTTP command on the endpoint
    '/napps/<username>/<name>' to delete the given NApp. A NApp can only be
    deleted by it's "owner".

    Parameters:
        username (string): Name of a user.
        name (string): NApp name.
    Returns
        HTTP code 200 if the NApp was successfully deleted.
        HTTP code 403 if there was permission problems.
        HTTP code 404 if the NApp was not found for the given username.
    """
    if user.username != username:
        return jsonify({"Your user can't delete this NApp" }), 401

    try:
        napp = user.get_napp_by_name(name)
    except NappsEntryDoesNotExists:
        msg = 'NApp {} not found for the user {}'.format(name, username)
        return jsonify({'error': msg}), 404

    try:
        napp.delete()
    except NappsEntryDoesNotExists:
        msg = 'Something went wrong while trying to delete the NApp {}/{}.'
        msg += msg.format(username, name)
        return jsonify({'error': msg}), 404

    msg = 'Napp {} was deleted.'
    return jsonify({'success': msg}), 200
