# System imports
import enum
import hashlib
import json
import os
import time

from copy import copy

from datetime import datetime
from datetime import timedelta

# Third-party imports
from flask import Flask
from itsdangerous import URLSafeTimedSerializer

# Local source tree imports
import config

app = Flask(__name__)
con = config.CON


# JSON Schema for Napps
napps_schema = {
    "git": {"type": "string"},
    "token":  {"type": "string"},
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



class User(object):
    """
    Class to manage Users
    """
    def __init__(self, username, password, email, first_name, last_name,
                 phone=None, city=None, state=None, country=None, enabled=False):
        self.username = username
        self.password = password # TODO: Crypt this
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.city = city
        self.state = state
        self.country = country
        self.enabled = enabled

    @property
    def redis_key(self):
        return "author:%s" % self.username

    @property
    def token(self):
        key = con.lrange("%s:tokens" % self.redis_key, 0, 0)[0]
        attributes = con.hgetall(key)
        token = Token()
        token.hash = attributes['hash']
        token.created_at = datetime.strptime(attributes['created_at'], '%Y-%m-%d %H:%M:%S.%f')
        token.expires_at = datetime.strptime(attributes['expires_at'], '%Y-%m-%d %H:%M:%S.%f')
        if token.is_valid():
            return token
        else:
            return None

    @classmethod
    def get(self, username):
        user = con.hgetall("author:%s" % username)
        if user:
            # TODO: Fix this hardcode attributes
            return User(user['username'], user['password'], user['email'],
                        user['first_name'], user['last_name'], user['phone'],
                        user['city'], user['state'], user['country'],
                        eval(user['enabled']))
        else:
            raise NappsEntryDoesNotExists("Username not found.")

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True

    def as_dict(self, hide_sensible=True, detailed=False):
        result = copy(self.__dict__)
        if hide_sensible:
            del result['password']

        if detailed:
            result['apps'] = "%s:apps" % self.redis_key
            result['comments'] = "%s:comments" % self.redis_key
            result['tokens'] = "%s:tokens" % self.redis_key

        return result

    def as_json(self, hide_sensible=True, detailed=False):
        return json.dumps(self.as_dict(hide_sensible, detailed))

    def save(self):
        """ Save a object into redis database.

        This is a save/update method. If the user already exists then update.
        """
        con.sadd("authors", self.redis_key)
        con.hmset(self.redis_key, self.as_dict(hide_sensible=False,
                                               detailed=True))

    def create_token(self, expiration_time=86400):
        token = Token()
        attributes = token.as_dict()
        attributes['username'] = self.username

        con.lpush("%s:tokens" % self.redis_key, "token:%s" % token.hash)
        con.hmset("token:%s" % token.hash, attributes)
        return token


class Token:
    """
    Class to manage Tokens
    """

    def __init__(self, expiration_time=86400):
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expiration_time)
        self.hash = self.generate()

    def is_valid(self):
        return datetime.utcnow() <= self.expires_at

    def generate(self):
        return hashlib.sha256(os.urandom(128)).hexdigest()

    def as_dict(self):
        return self.__dict__

    def as_json(self):
        return json.dumps(self.as_dict())


class NappsDuplicateEntry(Exception):
    pass

class NappsEntryDoesNotExists(Exception):
    pass
