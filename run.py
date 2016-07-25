# System imports
from datetime import timedelta

# Third-party imports

# Local source tree imports
from api import auth
from api import logout
from api import users
from api import napps
from api import comments
from api import common

# Expose login and logout endpoints
common.app.register_blueprint(auth.api)
common.app.register_blueprint(logout.api)

# Expose user endpoints
common.app.register_blueprint(users.api)

# Expose application endpoints
common.app.register_blueprint(napps.api)

# Expose comments endpoints
common.app.register_blueprint(comments.api)

if __name__ == '__main__':
    common.app.run(debug=True)
    common.app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)

    common.login_manager.login_view = "/api/login/"
    common.login_manager.setup_app(common.app)
    common.app.run()
