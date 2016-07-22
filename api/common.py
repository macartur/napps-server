# System imports
import hashlib
import os
import time

# Third-party imports
from flask import Flask
from flask.ext.login import LoginManager, UserMixin
from itsdangerous import URLSafeTimedSerializer
from flask.ext.principal import Principal
from flask.ext.principal import Permission
from flask.ext.principal import RoleNeed

# Local source tree imports
import config

app = Flask(__name__)
con = config.CON

# Authentication
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "a_random_secret_key_$%#!@"
login_serializer = URLSafeTimedSerializer(app.secret_key)

# Access Control
admin_permission = Permission(RoleNeed('admin'))

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


def get_token_key (login):
    """
    Returns the token key of a given user
    :param login: login name to check
    :return: Key in REDIS or None if user or key do not exist.
    """
    user_key = "author:"+login

    if con.sismember("authors", user_key):
        user_token_key = con.hget(user_key, "tokens")
        return user_token_key
    else:
        return None


def hash_pass(password):
    """
    Return the md5 hash of the password+salt
    :param password: password to be converted
    :return: password MD5
    """
    salted_password = password + app.secret_key
    return hashlib.md5(salted_password.encode()).hexdigest()


class Users:
    """
    Class to manage Users
    """
    def __init__(self, login):
        self.login = login

    def tokens(self):
        """
        This method returns a list with all tokens of a given user.
        :return: List of all tokens of the user
        """
        pass

    @property
    def hash_pass(self):
        """
        This method returns the hashed password of a given user
        :return: Hashed password
        """
        pass

    def user_role(self):
        """
        This method returns the role of a given user in system
        :return: Role name (admin or user)
        """
        pass


class Tokens:
    """
    Class to manage Tokens
    """

    def __init__(self, login=None, token=None):
        self.login = login
        self.token = token

    @property
    def token_gen(self):
        """
        Generates a new 256 bits token and store it in REDIs
        :return: a tuple with token and expiration epoch
        """
        new_hash = hashlib.sha256(os.urandom(128)).hexdigest()
        gen_time = int(time.time())
        token_expiration = int(time.time()) + 900

        # Token key in redis is the token itself
        token_key = get_token_key(self.login)
        if token_key is not None:
            con.sadd(token_key, new_hash)
            token_hash = {'login': self.login, 'expire': token_expiration, 'creation': gen_time}
            con.hmset(new_hash, token_hash)
        else:
            return None

        return (new_hash, token_expiration)

    def token_is_expired(self):
        """
        This method verifies if a given token is already expired or not.
        :return: True if expired or an integer with seconds remaing to expire.
        """
        curr_time = int(time.time())

        # Retrieve the token data
        token_to_validate = con.hgetall(self.token)

        time_to_expire = int(token_to_validate["expire"]) - curr_time
        if time_to_expire <= 0:
            return True
        else:
            return time_to_expire

    def token_to_login(self):
        """
        This method returns the user login given a specific token
        :return: Login of the token owner or None if token doesnt exist.
        """
        token_to_translate = con.hgetall(self.token)
        return token_to_translate["login"]
