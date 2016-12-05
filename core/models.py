# System imports
from copy import copy
from datetime import datetime
from datetime import timedelta
from docutils import core

import bcrypt
import config
import hashlib
import json
import os
import re
import smtplib
from urllib.request import urlopen

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Third-party imports
from jinja2 import Template

# Local source tree imports
from core.exceptions import NappsEntryDoesNotExists
from core.exceptions import InvalidAuthor
from core.exceptions import InvalidNappMetaData

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
        self.password = bcrypt.hashpw(password, bcrypt.gensalt()) # TODO: Crypt this
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
        return "user:{}".format(self.username)

    @property
    def token(self):
        try:
            key = con.lrange("%s:tokens" % self.redis_key, 0, 0)[0]
        except IndexError:
            return None

        attributes = con.hgetall(key)
        token = Token.from_dict(attributes)
        if token.is_valid():
            return token
        else:
            return None

    @classmethod
    def get(cls, username):
        attributes = con.hgetall("user:%s" % username)
        if attributes:
            return User.from_dict(attributes)
        else:
            raise NappsEntryDoesNotExists("User {} not found.".format(username))

    @classmethod
    def all(cls):
        users = con.smembers("users")
        return [User.from_dict(con.hgetall(user)) for user in users]

    @classmethod
    def check_auth(cls, username, password):
        try:
            user = User.get(username)
        except NappsEntryDoesNotExists:
            return False

        if bcrypt.checkpw(password, user.password):
            return False
        return True

    @classmethod
    def from_dict(cls, attributes):
        # TODO: Fix this hardcode attributes
        return User(attributes['username'], attributes['password'],
                    attributes['email'], attributes['first_name'],
                    attributes['last_name'], attributes['phone'],
                    attributes['city'], attributes['state'],
                    attributes['country'], eval(attributes['enabled']))

    def disable(self):
        self.enabled = False
        token = self.token
        token.invalidate()
        self.save()

    def enable(self):
        self.enabled = True
        self.save()

    def as_dict(self, hide_sensible=True, detailed=False):
        result = copy(self.__dict__)
        if hide_sensible:
            del result['password']

        if detailed:
            result['napps'] = "%s:napps" % self.redis_key
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
        token = Token(user=self, expiration_time=expiration_time)
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

    def get_all_napps(self):
        napps = con.smembers("%s:napps" % self.redis_key)
        result = []
        # TODO: Improve this
        for napp in napps:
            attributes = con.hgetall(napp)
            napp_object = Napp()
            napp_object.name = attributes['name']
            napp_object.description = attributes['description']
            napp_object.license = attributes['license']
            napp_object.git = attributes['git']
            napp_object.version = attributes['version']
            napp_object.user = User.get(attributes['user'])
            napp_object.tags = attributes['tags']
            result.append(napp_object)
        return result

    def get_napp_by_name(self, name):
      napps = self.get_all_napps()
      for napp in napps:
        if napp.name == name:
          return napp
      return None

    # TODO: Remove this from this class
    def render_template(self, filename, context):
        with open(os.path.join(TEMPLATE_DIR, filename), 'r') as f:
            template = Template(f.read())
            return template.render(context)


class Token(object):
    """
    Class to manage Tokens
    """

    def __init__(self, hash=None, created_at=None, user=None, expiration_time=86400):
        self.hash = hash if hash else self.generate()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.user = user
        self.expiration_time = expiration_time

    @property
    def redis_key(self):
        return "token:{}".format(self.hash)

    @property
    def expires_at(self):
        return self.created_at + timedelta(seconds=self.expiration_time)

    @classmethod
    def from_dict(cls, attributes):
        # TODO: Fix this hardcode attributes
        return Token(attributes['hash'],
                     datetime.strptime(attributes['created_at'], '%Y-%m-%d %H:%M:%S.%f'),
                     User.get(attributes['user']),
                     int(attributes['expiration_time']))

    @classmethod
    def get(cls, token):
        attributes = con.hgetall("token:%s" % token)
        if attributes:
            return Token.from_dict(attributes)
        else:
            raise NappsEntryDoesNotExists("Token not found.")

    def is_valid(self):
        return datetime.utcnow() <= self.expires_at

    def generate(self):
        return hashlib.sha256(os.urandom(128)).hexdigest()

    def invalidate(self):
        self.expiration_time = 0
        self.save()

    def as_dict(self):
        dict = copy(self.__dict__)
        dict['user'] = self.user.username
        return dict

    def as_json(self):
        return json.dumps(self.as_dict())

    def assign_to_user(self, user):
        self.user = user

    def save(self):
        """ Save a object into redis database.

        This is a save/update method. If the token exists then update.
        """
        con.sadd("tokens", self.redis_key)
        con.hmset(self.redis_key, self.as_dict())


class Napp(object):

    schema = {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "long_description": {"type": "string"},
        "version": {"type": "string"},
        "author": {"type": "string"},
        "license": {"type": "string"},
        "git": {"type": "string"},
        "branch": {"type": "string"},
        "ofversion": {"type": "array",
                      "items": { "type": "string" },
                      "minItems": 1,
                      "uniqueItems": True },
        "tags": {"type": "array",
                 "items": { "type": "string" },
                 "minItems": 1,
                 "uniqueItems": True },
        "dependencies": {"type": "array",
                         "items": { "type": "string" },
                         "minItems": 0,
                         "uniqueItems": True },
        "required": ["name", "description", "version", "author","license",
                     "git", "branch", "ofversion", "tags", "dependencies"]
    }

    def __init__(self, content, user=None):
        if user is not None:
            if not isinstance(user, User):
                user = User.get(user)
            self.user = user
        if content is not None:
            self._populate_from_dict(content)

    @property
    def redis_key(self):
        return "napp:{}/{}".formata(self.author, self.name)

    @property
    def _url_for_raw_file_from_git(self):
        url = re.sub('\.git\/?$', '/', self.git)
        url += "raw/" + self.branch + "/" + self.author + "/"
        url += self.name + "/"
        return url

    @property
    def json_from_git(self):
        url = self._url_for_raw_file_from_git + 'kytos.json'
        buffer = urlopen(url)
        metadata = str(buffer.read(), encoding="utf-8")
        attributes = json.loads(metadata)
        return attributes

    @property
    def readme_rst_from_git(self):
        url = self._url_for_raw_file_from_git + 'README.rst'
        try:
            buffer = urlopen(url)
            readme = str(buffer.read(), encoding="utf-8")
            return readme
        except:
            return ''

    @property
    def readme_html_from_git(self):
        readme = self.readme_rst_from_git
        if readme:
            parts = core.publish_parts(source=self.readme_rst_from_git,
                                       writer_name='html')
            return parts['body_pre_docinfo'] + parts['fragment']
        else:
            return ''

    @classmethod
    def all(cls):
        napps = con.smembers("napps")
        result = []
        # TODO: Improve this
        for napp in napps:
            attributes = con.hgetall(napp)
            napp_object = Napp(attributes)
            result.append(napp_object)
        return result

    def _populate_from_dict(self, attributes):
        for key in self.schema.keys():
            if key != 'required':
                # This is a validation for required items...
                # But it can be improved
                if key in self.schema['required'] and key not in attributes:
                    raise InvalidNappMetaData('Missing key {}'.format(key))
                setattr(self, key, attributes.get(key))

    @classmethod
    def new_napp_from_dict(cls, attributes, user):
        napp = cls(attributes, user)
        if napp.user.username != napp.author:
            raise InvalidAuthor
        else:
            napp.save()
            return napp

    def update_from_dict(self, attributes):
        if self.user.username != attributes.author:
            raise InvalidAuthor
        else:
            self._populate_from_dict(attributes)
            self.save()

    def update_from_git(self):
        self.update_from_dict(self.json_from_git)

    def as_dict(self):
        data = copy(self.__dict__)
        data['user'] = self.user.username
        data['readme'] = self.readme_html_from_git
        return data

    def as_json(self):
        data = self.as_dict()
        data['tags'] = self.tags.split(',')
        return json.dumps(data)

    def save(self):
        """ Save a object into redis database.

        This is a save/update method. If the app exists then update.
        """
        con.sadd("napps", self.redis_key)
        con.sadd("user:%s:napps" % self.author, self.redis_key)
        con.hmset(self.redis_key, self.as_dict())
