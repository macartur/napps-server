from flask import Flask

from api import users
from api import napps
from api import comments

app = Flask(__name__)

# Expose user endpoints
app.register_blueprint(users.api)

# Expose application endpoints
app.register_blueprint(napps.api)

# Expose comments endpoints
app.register_blueprint(comments.api)

if __name__ == '__main__':
    app.run(debug=True)
