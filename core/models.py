# System imports
from copy import copy
from datetime import datetime
from datetime import timedelta

import config
import hashlib
import json
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Third-party imports
from jinja2 import Template

# Local source tree imports
from core.exceptions import NappsEntryDoesNotExists

con = config.CON

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(APP_ROOT, 'templates')

class User(object):
    """
    Class to manage Users
    """
    schema = {
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "password": {"type": "string"},
        "email": {"type": "string"},
        "phone": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "country": {"type": "string"},
        "required": ["username", "first_name", "last_name", "password", "email"]
    }

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
        return "user:%s" % self.username

    @property
    def token(self):
        try:
            key = con.lrange("%s:tokens" % self.redis_key, 0, 0)[0]
        except IndexError:
            return None

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
        attributes = con.hgetall("user:%s" % username)
        if attributes:
            return User.from_dict(attributes)
        else:
            raise NappsEntryDoesNotExists("Username not found.")

    @classmethod
    def all(self):
        users = con.smembers("users")
        return [User.from_dict(con.hgetall(user)) for user in users]

    @classmethod
    def check_auth(uself, username, password):
        try:
            user = User.get(username)
        except NappsEntryDoesNotExists:
            return False

        if user.password != password:
            return False
        return True

    @classmethod
    def from_dict(self, attributes):
        # TODO: Fix this hardcode attributes
        return User(attributes['username'], attributes['password'],
                    attributes['email'], attributes['first_name'],
                    attributes['last_name'], attributes['phone'],
                    attributes['city'], attributes['state'],
                    attributes['country'], eval(attributes['enabled']))

    def disable(self):
        self.enabled = False
        self.save()

    def enable(self):
        self.enabled = True
        self.save()

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
        con.sadd("users", self.redis_key)
        con.hmset(self.redis_key, self.as_dict(hide_sensible=False,
                                               detailed=True))

    def create_token(self, expiration_time=86400):
        token = Token(username=self.username)
        token.save()
        con.lpush("%s:tokens" % self.redis_key, token.redis_key)
        return token

    def send_email(self, template, subject):
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = 'no-reply@kytos.io'
            message['To'] = self.email
            part1 = MIMEText(template, 'html')
            message.attach(part1)
            smtp = smtplib.SMTP('localhost')
            smtp.sendmail('no-reply@kytos.io', self.email, message.as_string())
            smtp.quit()

    def send_token(self):
        if not self.token:
            return False

        context = {'username': self.username,
                   'token': self.token.hash}

        html = self.render_template('confirm_user.phtml', context)
        self.send_email(html, 'Kytos Napps Repository: Confirm your account')

    def send_welcome(self):
        if not self.enabled:
            return False

        context = {'username': self.username}
        html = self.render_template('welcome.phtml', context)
        self.send_email(html, 'Welcome to Kytos Napps Respository')

    # TODO: Remove this from this class
    def render_template(self, filename, context):
        with open(os.path.join(TEMPLATE_DIR, filename), 'r') as f:
            template = Template(f.read())
            return template.render(context)

class Token(object):
    """
    Class to manage Tokens
    """

    def __init__(self, username=None, expiration_time=86400):
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(seconds=expiration_time)
        self.hash = self.generate()
        self.username = username

    @property
    def redis_key(self):
        return "token:%s" % self.hash

    def is_valid(self):
        return datetime.utcnow() <= self.expires_at

    def generate(self):
        return hashlib.sha256(os.urandom(128)).hexdigest()

    def invalidate(self):
        self.expires_at = datetime.utcnow()
        self.save()

    def as_dict(self):
        return self.__dict__

    def as_json(self):
        return json.dumps(self.as_dict())

    def assign_to_user(self, username):
        self.username = username

    def save(self):
        """ Save a object into redis database.

        This is a save/update method. If the token exists then update.
        """
        con.sadd("tokens", self.redis_key)
        con.hmset(self.redis_key, self.as_dict())
