# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

# Flask Blueprints
napps_api = Blueprint('napps_api', __name__)
napp_api = Blueprint('napp_api', __name__)

con = config.CON


@napps_api.route('/apps/', methods=['GET'])
def get_apps():
    """
    This routine creates an endpoint that shows details about all applications.
    It returns all information in JSON format.
    """

    # app_dict = {"app": {}}
    app_dict = {}
    app_names = con.smembers("apps")

    for app_name in app_names:
        app_dict[app_name] = con.hgetall(app_name)
        app_dict[app_name]["author"] = con.hgetall(con.hget(app_name,
                                                                   "author"))
        app_dict[app_name]["ofversions"] = list(con.smembers
                                                       (con.hget
                                                        (app_name,
                                                         "ofversions")))
        app_dict[app_name]["tags"] = list(con.smembers
                                                 (con.hget(app_name,
                                                           "tags")))
        app_dict[app_name]["versions"] = list(con.smembers
                                                     (con.hget
                                                      (app_name,
                                                       "versions")))
        app_dict[app_name]["comments"] = con.scard(con.hget(app_name,
                                                                   "comments"))
    return jsonify({'apps': app_dict})


@napp_api.route('/apps/<name>', methods=['GET'])
def get_app(name):
    """
    This routine creates an endpoint that shows details about a specific
    application. It returns all information in JSON format.
    """

    # app_dict = {"app": {}}
    app_dict = {}
    app_dict[name] = con.hgetall("app:"+name)
    app_dict[name]["author"] = con.hgetall(con.hget
                                                ("app:"+name, "author"))
    app_dict[name]["ofversions"] = list(con.smembers
                                               (con.hget
                                                ("app:"+name, "ofversions")))
    app_dict[name]["tags"] = list(con.smembers
                                         (con.hget("app:"+name, "tags")))
    app_dict[name]["versions"] = list(con.smembers
                                             (con.hget
                                              ("app:"+name, "versions")))

    return jsonify({'app': app_dict})
