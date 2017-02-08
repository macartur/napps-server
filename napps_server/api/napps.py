"""Module used to make avaliable napps routes."""
# System imports
import os
import re
from time import strftime

# Third-party imports
from flask import Blueprint, Response, jsonify, request

from napps_server.core.decorators import requires_token, validate_json
from napps_server.core.exceptions import (InvalidAuthor, InvalidNappMetaData,
                                          NappsEntryDoesNotExists)
# Local source tree imports
from napps_server.core.models import Napp, User

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


def _napp_versioned_name(author, napp_name):
    """Build the napp filename with a timestamp and a counter."""
    author_repo = os.path.join(NAPP_REPO, author)
    basename = napp_name + '-' + _curr_date() + '-'
    regexp = re.compile(r'' + basename + '(\d+)' + '.napp')
    counter = 0
    for file in os.listdir(author_repo):
        matched = regexp.match(file)
        if matched and int(matched.group(1)) > counter:
            counter = int(matched.group(1))
    return basename + str(counter + 1) + '.napp'


def _from_ImmutableMultiDict_to_dict(immd):
    """Method that converts an ImmutableMultiDict to a dict.

    This convertion consider the expected type of each attribute, based on the
    Napp.schema reference.
    """
    output = dict()
    for key in Napp.schema:
        if key != 'required' and key != 'user':
            # This ia a validation for required items...
            # But it can be improved
            if key in Napp.schema['required'] and key not in immd:
                raise InvalidNappMetaData('Missing key {}'.format(key))

            # Converting to list
            if Napp.schema[key]['type'] == 'array':
                output[key] = immd.getlist(key)
            else:
                output[key] = immd[key]

    return output


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
    #: As we expect here a multipart/form POST, then the 'data' may come on the
    #: form attribute of the request, instead of the json attribute.
    content = _from_ImmutableMultiDict_to_dict(request.form)

    # Get the name of the uploaded file
    sent_file = request.files['file']

    if not user.enabled or not content['author'] == user.username:
        return Response("Permission denied", 401)
    elif not sent_file or not _allowed_file(sent_file.filename):
        return Response("Invalid file/file extension.", 401)

    try:
        Napp.new_napp_from_dict(content, user)
    except InvalidAuthor:
        return Response("Permission denied. Invalid Author.", 401)
    except InvalidNappMetaData:
        return Response("Permission denied. Invalid metadata.", 401)

    author_repo = os.path.join(NAPP_REPO, content['author'])
    os.makedirs(author_repo, exist_ok=True)
    napp_latest = content['name'] + '-latest.napp'
    napp_filename = _napp_versioned_name(content['author'], content['name'])
    # Move the file form the temporal folder to
    # the upload folder we setup
    sent_file.save(os.path.join(author_repo, napp_filename))

    # Updating the 'latest' version, symbolic linking it to the uploaded file.
    try:
        os.remove(os.path.join(author_repo, napp_latest))
    except FileNotFoundError:
        pass
    os.symlink(os.path.join(author_repo, napp_filename),
               os.path.join(author_repo, napp_latest))

    return Response("Napp succesfully created", 201)


@api.route('/napps/<author>/<name>/', methods=['DELETE'])
def delete_napp(author, name):
    """Method used to show a detailed napp information.

    This method creates the '/napps/<author>/<name>' endpoint that shows a
    detailed napp information as a json format.

    Parameters:
        author (string): Author name.
        name (string): Napp name.
    Returns
        json (string): String with all information in JSON format.
    """
    content = request.get_json()
    token = content.get('token', None)

    try:
        user = User.get(author)
    except NappsEntryDoesNotExists:
        return jsonify({
            'error': 'Author {} not found'.format(author)
        }), 404

    try:
        napp = user.get_napp_by_name(name)
    except NappsEntryDoesNotExists:
        msg = 'NApp {} not found for the author {}'.format(name, author)
        return jsonify({'error': msg}), 404

    if token != user.token.hash:
        msg = 'Napp can\'t be deleted by the author {} '.format(name, author)
        return jsonify({'error': msg}), 404

    try:
        napp.delete()
    except NappsEntryDoesNotExists:
        msg = 'Napp {} can\'t be deleted.'.format(name)
        return  jsonify({'error': msg }), 404

    msg = 'Napp {} was deleted.'
    return jsonify({'success': msg}), 200
