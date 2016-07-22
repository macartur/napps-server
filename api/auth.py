# System imports

# Third-party imports
from flask import Blueprint
from flask import request
from flask import jsonify
from jsonschema import validate
from jsonschema import ValidationError

# Local source tree imports
import config
from api import common

con = config.CON


# Flask Blueprints
api = Blueprint('auth_api', __name__)


@api.route("/api/auth/", methods=["GET", "POST"])
def login_page():
    """
    Endpoint to perform the authentication
    :return: page requested or /napps endpoint
    """
    if request.method == "POST":
        user = common.User.get(request.form['username'])

        if user and common.hash_pass(request.form['password']) == \
                user.password:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or "/api/napps/")

    return render_template("login.html")
