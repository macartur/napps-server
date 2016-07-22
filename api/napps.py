# System imports

# Third-party imports
from jsonschema import validate
from jsonschema import ValidationError
from flask import Blueprint
from flask import request
from flask import jsonify


# Local source tree imports
import config
from api import common

con = config.CON


# Flask Blueprints
api = Blueprint('napps_api', __name__)

# Routines

def get_author(app_name):
    """
    Gather all information about a given napp's author.
    :param app_name: name of the napp to retrieve author data
    :return: return a dict with author's data
    """
    exclude = ['phone', 'pass', 'email', 'comments', 'apps', 'tokens', 'role']
    author = con.hgetall(con.hget(app_name, "author"))

    for item in exclude:
        author.pop(item, None)
    return author


def get_redis_list(name, key):
    """
    Return a list type from REDIs DB.
    :param name: name of the list
    :param key: the key to return
    :return: returns a list type
    """
    return list(con.smembers(con.hget(name,key)))


# TODO: Define some returns or exceptions to this procedure.
def napp_git_download(git_url, login):
    """
    This routine is used to download, parse and store a json file located
    in the napp repo and adds it to the login apps tree.
    :param git_url: url of the napp git repo
    :param login: user login to be used to add the napp
    :return: 0 if all process worked fine
    """
    return 0

# Endpoints Definitions

@api.route('/api/napps/<name>', methods=['GET'])
def get_app(name):
    """
    This routine creates an endpoint that shows details about a specific
    application. It returns all information in JSON format.
    """

    app_key = "app:"+name
    app = con.hgetall(app_key)
    app["author"] = get_author(app_key)
    app["ofversions"] = get_redis_list(app_key, "ofversions")
    app["tags"] = get_redis_list(app_key, "tags")
    app["versions"] = get_redis_list(app_key, "versions")
    app["comments"] = con.scard(con.hget(name, "comments"))

    return jsonify({'napp': app})


@api.route('/api/napps/', methods=['GET', 'POST'])
def get_apps():
    """
    This routine creates an endpoint that shows details about all applications.
    It returns all information in JSON format.
    """
    if request.method == "GET":
        apps = {}
        for name in con.smembers("apps"):
            app = con.hgetall(name)
            app["author"] = get_author(name)
            app["ofversions"] = get_redis_list(name, "ofversions")
            app["tags"] = get_redis_list(name, "tags")
            app["comments"] = con.scard(con.hget(name, "comments"))
            apps[name] = app

        return jsonify({'napps': apps})

    elif request.method == "POST":
        content = request.get_json(silent=True)
        try:
            validate(content, common.napps_schema)
            token_sent = common.Tokens(token_id=content['token'])
            current_user = common.Users(login=token_sent.token_to_login())

            if token_sent.token_is_expired():
                return '', 400
            else:
                napp_git_download(content['git'], current_user.login)
                return '', 200
        except ValidationError:
            return '', 401
