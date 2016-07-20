# System imports

# Third-party imports
from flask import Blueprint
from flask import request
from flask import redirect
from flask import render_template
from flask_login import login_user

# Local source tree imports
import config
from api import common

con = config.CON


# Flask Blueprints
api = Blueprint('login_api', __name__)


@api.route("/login/", methods=["GET", "POST"])
def login_page():
    """
    Endpoint to perform the authentication
    :return:
    """
    if request.method == "POST":
        user = common.User.get(request.form['username'])

        if user and common.hash_pass(request.form['password']) == \
                user.password:
            login_user(user, remember=True)
            return redirect(request.args.get("next") or "/napps/")

    return render_template("login.html")
