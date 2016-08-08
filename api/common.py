# System imports
import hashlib
import os
import time

# Third-party imports
from flask import Flask
from itsdangerous import URLSafeTimedSerializer
from flask.ext.principal import Permission
from flask.ext.principal import RoleNeed

# Local source tree imports
import config

app = Flask(__name__)
con = config.CON

# Authentication
app.secret_key = "a_random_secret_key_$%#!@"
login_serializer = URLSafeTimedSerializer(app.secret_key)

# Access Control
admin_permission = Permission(RoleNeed('admin'))

# JSON Schema for Napps
napps_schema = {
    "git": {"type": "string"},
    "token":  {"type" : "string"},
    "required": ["git", "token"]}

# JSON Schema for authentication
napps_auth = {
    "login": {"type": "string"},
    "password": {"type": "string"},
    "required": ["login", "password"]}

# JSON Schema for Napps Description
napp_git_schema = {
    "napp": {
            "name": {"type": "string"},
            "version": {"type": "string"},
            "ofversion": {"type": "string"},
            "dependencies": {"type": "string"},
            "description": {"type": "string"},
            "license": {"type": "string"},
            "git": {"type": "string"},
            "tags": {"type": "array"},
            "required": ["name", "version", "ofversion", "license"]
    },
    "required": ["napp"]
}

# JSON Schema to Add New Authors
napp_git_author = {
            "login": {"type": "string"},
            "name": {"type": "string"},
            "pass": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"},
            "city": {"type": "string"},
            "state": {"type": "string"},
            "country": {"type": "string"},
            "required": ["login", "name", "pass", "email", "country"]
}


def token_gen(type):
    """
    Routine to generate a token of a given type
    :param type: Can be Auth or Validation token
    :return: A token object
    """
    if type is "Auth":
        token_expiration_sec = 900
    elif type is "Validation":
        token_expiration_sec = 86400
    else:
        return False

    gen_time = int(time.time())
    token_expiration = int(time.time()) + token_expiration_sec
    new_hash = hashlib.sha256(os.urandom(128)).hexdigest()

    new_token = Token(token_exp_time=token_expiration,
                      token_gen_time=gen_time,
                      token_id=new_hash,
                      token_type=type)
    return new_token


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


class User:
    """
    Class to manage Users
    """
    def __init__(self, login):
        self.__login = login

    def has_token(self, token):
        """
        This method verifies if a given token is owned by the user.
        :param token: The token to be checked
        :return: True if token is owned by the user or false if not
        """

        token_key = get_token_key(self.login)
        if con.sismember(token_key, token):
            return True
        return False

    @property
    def login(self):
        """
        Returns the login name of the object
        :return: User login
        """
        return self.__login

    @property
    def hash_pass(self):
        """
        This method returns the hashed password stored in redis
        :return: Hashed password
        """
        author_key = "author:"+self.login
        return con.hget(author_key, "pass")

    @property
    def is_active(self):
        """
        This method verifies the status of a given user.
        :return: True is user is active or False if not
        """
        author_key = "author:"+self.login
        if con.hget(author_key, "status") == "active":
            return True
        else:
            return False

    def user_role(self):
        """
        This method returns the role of a given user in system
        :return: Role name (admin or user)
        """
        author_key = "author:"+self.login
        return con.hget(author_key, "role")


class Token:
    """
    Class to manage Tokens
    """

    def __init__(self, token_exp_time, token_gen_time, token_id=None, token_type="Auth"):
        self.__token_id = token_id
        self.__token_exp_time = token_exp_time
        self.__token_gen_time = token_gen_time
        self.__token_type = token_type

    @property
    def token_id(self):
        return self.__token_id

    @property
    def token_exp_time(self):
        return int(self.__token_exp_time)

    @property
    def token_gen_time(self):
        return int(self.__token_gen_time)

    @property
    def token_type(self):
        return self.__token_type

    def token_valid(self):
        """
        This method verifies if a given token is already expired or not.
        :return: False if token is expired or remaining time to expiration in seconds.
        """
        if self.token_id is not None and self.token_exist():
            curr_time = int(time.time())

            # Retrieve the token data
            token_to_validate = con.hgetall(self.token_id)

            time_to_expire = int(token_to_validate['expire']) - curr_time
            if time_to_expire <= 0:
                return False
            else:
                return time_to_expire
        else:
            return False

    def token_exist(self):
        """
        This method checks if token exists in REDIs
        :return: True if token exists or false if not
        """
        token_dict = con.hgetall(self.token_id)
        return any(token_dict)

    def token_to_login(self):
        """
        This method returns the user login given a specific token
        :return: Login of the token owner or None if token doesnt exist.
        """
        if self.token_id is not None and self.token_exist():
            token_to_translate = con.hgetall(self.token_id)
            return token_to_translate['login']
        else:
            return None
