"""Module to manager users."""
# System imports

# Third-party imports

# Local source tree imports
from flask import Blueprint, jsonify, redirect, request, Response

from napps_server.core.decorators import (requires_token, validate_json,
                                          validate_schema)
from napps_server.core.exceptions import NappsEntryDoesNotExists
from napps_server.core.models import User
from napps_server.core.utils import get_request_data

# Flask Blueprints
api = Blueprint('user_api', __name__)


@api.route("/users/", methods=["POST"])
@validate_json
@validate_schema(User.schema)
def register_user():
    """Method used to register new user into the system.

    This method will register  '/users/' endpoint and receive POST requests.
    If the username already exists will return a JSON with a error message and
    HTTP code 401, otherwise will return HTTP code 201 and a empty string.

    Returns:
        json (string): JSON with result of user registration.
    """
    content = get_request_data(request, User.schema)

    try:
        User.get(content.get('username'))
        return Response("error: Username already exists", 403)
    except NappsEntryDoesNotExists:
        user = User(username=content.get('username', ''),
                    email=content.get('email', ''),
                    first_name=content.get('first_name', ''),
                    last_name=content.get('last_name', ''),
                    phone=content.get('phone', None),
                    city=content.get('city', None),
                    state=content.get('state', None),
                    country=content.get('country', None))

        user.set_password(content['password'])
        user.save()
        user.create_token()
        user.send_token()
        return Response('User successfully created.', 201)


@api.route('/users/', methods=['GET'])
def get_users():
    """Method used to show all applications developers.

    This method will creates '/users/' endpoint that shows all application
    author usernames with their informations.

    Returns:
        json (string): JSON with detailed users.
    """
    users = {user.username: user.as_dict() for user in User.all()}
    return jsonify({'users': users}), 200


@api.route('/users/<username>/', methods=['GET'])
def get_user(username):
    """Method used to show details about a specific user.

    This method creates '/users/<username>/' endpoint that shows details
    about a specific application author. If the username can't be found
    by system will return HTTP code 404 and a error message. Otherwise will
    return the HTTP code 200 and render a json with user informations.

    Parameters:
        username (string): Name of a user.
    Returns:
        json (string): JSON with all information about a specific author.
    """
    try:
        user = User.get(username)
    except NappsEntryDoesNotExists:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.as_dict()), 200


@api.route("/users/<username>/confirm/<token>/", methods=["GET"])
def confirm_user(username, token):
    """Method used to confirm the user and his token.

    This method will get a username and a token and verify if they are valid.
    If these are invalid must return the HTTP code 40X and a JSON with the
    message error. Otherwise must return the HTTP code 200.

    Parameters:
        username (string):  Name of a user.
        token (string): valid token.
    Returns:
        json (string): JSON with error message.
    """
    # Check if user exists
    url = 'http://napps.kytos.io?{}'

    try:
        user = User.get(username)
    except NappsEntryDoesNotExists:
        return redirect(url.format("user_not_found"), code=307)

    if not user.token:
        return redirect(url.format('invalid_token'), code=307)

    # Check if token belongs to user and is a valid token
    if (user.token.hash != token) or (not user.token.is_valid()):
        return redirect(url.format('invalid_token'), code=307)

    user.enable()
    user.token.invalidate()
    user.send_welcome()
    return redirect(url.format('activated'), code=307)


# @api.route("/users/<username>/", methods=['DELETE'])
def delete_user(username):
    """Method used to create a endpoint to delete a user.

    The endpoint created is /users/<username>/
    """
    content = get_request_data(request, User.schema)
    token = content.get('token', None)

    try:
        user = User.get(username)
    except NappsEntryDoesNotExists:
        error_msg = "User {} not found.".format(username)
        return jsonify({"error": error_msg}), 404

    if token != user.token.hash:
        msg = "The user {} can't be deleted using the token {}."
        return jsonify({"error": msg.format(user.username, token)}), 404

    user.delete()
    msg = 'The user {} was deleted.'.format(username)
    return jsonify({'success': msg})
