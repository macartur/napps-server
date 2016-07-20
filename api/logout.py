# System imports

# Third-party imports
from flask import Blueprint
from flask import request
from flask import redirect
from flask import session
from flask import current_app
from flask_login import login_required
from flask.ext.login import logout_user
from flask.ext.principal import AnonymousIdentity
from flask.ext.principal import identity_changed

# Local source tree imports
import config

con = config.CON


# Flask Blueprints
api = Blueprint('logout_api', __name__)


@api.route("/logout/")
@login_required
def logout():
    """
    Endpoint to logout from the system
    :return:
    """
    logout_user()

    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())

    return redirect(request.args.get("next") or "/login/")
