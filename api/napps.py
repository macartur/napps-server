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
        apps[name] = con.hgetall(name)
        apps[name]["author"] = get_author(name)
        apps[name]["ofversions"] = get_redis_list(name, "ofversions")
        apps[name]["tags"] = get_redis_list(name, "tags")
        apps[name]["versions"] = get_redis_list(name, "versions")
        apps[name]["comments"] = con.scard(con.hget(name, "comments"))

    return jsonify({'napps': apps})


@api.route('/napps/<name>', methods=['GET'])
def get_app(name):
    """
    This routine creates an endpoint that shows details about a specific
    application. It returns all information in JSON format.
    """

    app = {}
    app_key = "app:"+name
    app[name] = con.hgetall(app_key)
    app[name]["author"] = get_author(app_key)
    app[name]["ofversions"] = get_redis_list(app_key,"ofversions")
    app[name]["tags"] = get_redis_list(app_key,"tags")
    app[name]["versions"] = get_redis_list(app_key, "versions")
    app[name]["comments"] = con.scard(con.hget(app_key, "comments"))

    return jsonify({'napp': app})
