"""Module to manager users."""
# System imports

import os
# Third-party imports
from flask import Blueprint, render_template

# Local source tree imports
from napps_server.core.models import User

UI_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(UI_ROOT, 'static')
TEMPLATE_DIR = os.path.join(UI_ROOT, 'templates')

# Flask Blueprints
app = Blueprint('user_ui', __name__,
                template_folder=TEMPLATE_DIR,
                static_folder=STATIC_FOLDER,
                static_url_path='/static/user_ui')

@app.route("/register/", methods=["GET"])
def new_user():
    """Method used to registered a new endpoint to provide a user registration.

    Returns:
       html_content (string), string with html content.
       status_code (int): response status code.
    """
    context = {'fields': user_fields(),
               'fields_required': User.schema['required']}
    return render_template("new_user.phtml", context=context), 200


def user_fields():
    """Method used to return user fields.

    This method will return a list with tuples, the first item is a name of
    field and the second item is a type of field.

    Returns:
        fields (list): python list with user fields.
    """
    return [("username", 'text'),
            ("first_name", 'text'),
            ("last_name", 'text'),
            ("password", 'password'),
            ("confirm_password", 'password'),
            ("email", 'email'),
            ("phone", 'tel'),
            ("city", 'text'),
            ("state", 'text'),
            ("country", 'text')]
