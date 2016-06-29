from flask import Flask
from flask import Response
from flask.ext.login import LoginManager, UserMixin, login_required

from api import users
from api import napps
from api import comments
from api import common

# Expose user endpoints
common.app.register_blueprint(users.api)

# Expose application endpoints
common.app.register_blueprint(napps.api)

# Expose comments endpoints
common.app.register_blueprint(comments.api)

if __name__ == '__main__':
    common.app.run(debug=True)
