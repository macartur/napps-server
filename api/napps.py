# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

con = config.CON


# Flask Blueprints
api = Blueprint('napps_api', __name__)


def get_author(app_name):
    exclude = ['phone', 'pass', 'email', 'comments', 'apps']
    author = con.hgetall(con.hget(app_name, "author"))

    for item in exclude:
        author.pop(item, None)
    return author


def get_redis_list(name, key):
    return list(con.smembers(con.hget(name,key)))


@api.route('/napps/', methods=['GET'])
def get_apps():
    """
    This routine creates an endpoint that shows details about all applications.
    It returns all information in JSON format.
    """

    apps = {}
    for name in con.smembers("apps"):
        app = con.hgetall(name)
        app["author"] = get_author(name)
        app["ofversions"] = get_redis_list(name, "ofversions")
        app["tags"] = get_redis_list(name, "tags")
        app["comments"] = con.scard(con.hget(name, "comments"))
        apps[name] = app

    return jsonify({'napps': apps})


@api.route('/napps/<name>', methods=['GET'])
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
