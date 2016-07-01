# System imports
import hashlib

# Third-party imports
from flask import Flask
from flask.ext.login import LoginManager, UserMixin
from itsdangerous import URLSafeTimedSerializer

# Local source tree imports
import config

app = Flask(__name__)
con = config.CON

# Authentication
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "a_random_secret_key_$%#!@"
login_serializer = URLSafeTimedSerializer(app.secret_key)

# JSON Schema for Napps
napps_schema = {
    "git": {"type": "string"},
    "token":  {"type" : "string"},
    "required": ["git", "token"]}

# JSON Schema for Napps Description
napp_git_schema = {
    "name": {"type": "string"},
    "description": {"type": "string"},
    "license": {"type": "string"},
    "ofversions": {"type": "string"},
    "version": {"type": "string"},
    "required": ["name", "license", "ofversions", "version"]}


class User(UserMixin):
    """
    User Class for flask-Login
    """

    def __init__(self, userid, password):
        self.id = userid
        self.password = password

    def get_auth_token(self):
        """
        Encode a secure token for cookie
        :return: encoded token
        """
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    @staticmethod
    def get(userid):
        """
        Static method to search in REDIS and see if userid exists.  If it
        does exist then return a User Object.  If not then return None as
        required by Flask-Login.
        :param userid: Userid to search for
        :return: A User Object if user exists or None if not.
        """

        user_key = "author:"+userid

        if con.sismember("authors", user_key):
            user_pass = con.hget(user_key, "pass")
            print(user_pass)
            return User(userid, user_pass)
        return None


def hash_pass(password):
    """
    Return the md5 hash of the password+salt
    :param password: password to be converted
    :return: password MD5
    """
    salted_password = password + app.secret_key
    return hashlib.md5(salted_password.encode()).hexdigest()


@login_manager.user_loader
def load_user(userid):
    """
    Flask-Login user_loader callback.
    The user_loader function asks this function to get a User Object or return
    None based on userid.
    The userid was stored in the session environment by Flask-Login.
    user_loader stores the returned User object in current_user during
    every flask request.
    :param userid: Userid of the current session
    :return: return a User object every request
    """
    return User.get(userid)


@login_manager.token_loader
def load_token(token):
    """
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process to check if it's valid and then return
    an User object if it's valid or None if it's not.
    :param token: token to be check the expiration
    :return: User object if token is valid or None if not
    """
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()
    data = login_serializer.loads(token, max_age=max_age)
    user = User.get(data[0])

    if user and data[1] == user.password:
        return user
    return None
