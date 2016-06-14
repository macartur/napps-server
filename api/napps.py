# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify

# Local source tree imports
import config

# Flask Blueprints
napps_api = Blueprint('napps_api', __name__)
napp_api = Blueprint('napp_api', __name__)

con = config.CON


@napps_api.route('/apps/', methods=['GET'])
def get_apps():
    app_dict = {"app": {}}
    app_names = con.smembers("apps")

    for app_name in app_names:
        app_dict["app"][app_name] = con.hgetall(app_name)
        app_dict["app"][app_name]["author"] = con.hgetall(con.hget(app_name,
                                                                   "author"))
        app_dict["app"][app_name]["ofversions"] = list(con.smembers
                                                       (con.hget
                                                        (app_name,
                                                         "ofversions")))
        app_dict["app"][app_name]["tags"] = list(con.smembers
                                                 (con.hget(app_name,
                                                           "tags")))
        app_dict["app"][app_name]["versions"] = list(con.smembers
                                                     (con.hget
                                                      (app_name,
                                                       "versions")))

    return jsonify(app_dict)


@napp_api.route('/apps/<name>', methods=['GET'])
def get_app(name):
    app_dict = {"app": {}}

    app_dict["app"][name] = con.hgetall("app:"+name)
    app_dict["app"][name]["author"] = con.hgetall(con.hget
                                                  ("app:"+name, "author"))
    app_dict["app"][name]["ofversions"] = list(con.smembers
                                               (con.hget
                                                ("app:"+name, "ofversions")))
    app_dict["app"][name]["tags"] = list(con.smembers
                                         (con.hget("app:"+name, "tags")))
    app_dict["app"][name]["versions"] = list(con.smembers
                                             (con.hget
                                              ("app:"+name, "versions")))

    return jsonify(app_dict)
