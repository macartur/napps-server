from flask import Flask

from api import users
from api import napps
from api import comments

app = Flask(__name__)

# Expose user endpoints
app.register_blueprint(users.user_api)
app.register_blueprint(users.users_api)

# Expose application endpoints
app.register_blueprint(napps.napps_api)
app.register_blueprint(napps.napp_api)

# Expose comments endpoints
app.register_blueprint(comments.comments_api)

if __name__ == '__main__':
    app.run(debug=True)
