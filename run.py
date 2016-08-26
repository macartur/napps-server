# System imports
from datetime import timedelta

# Third-party imports
from flask import Flask

# Local source tree imports
from api import auth
#from api import comments
#from api import common
from api import napps
from api import users

app = Flask(__name__)

# Expose login and logout endpoints
app.register_blueprint(auth.api)

# Expose user endpoints
app.register_blueprint(users.api)

# Expose application endpoints
app.register_blueprint(napps.api)

# Expose comments endpoints
#common.app.register_blueprint(comments.api)

if __name__ == '__main__':
    app.run(debug=True)
