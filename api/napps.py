# System imports

# Third-party imports
from jsonschema import validate
from jsonschema import ValidationError
from flask import Blueprint
from flask import request
from flask import jsonify
import urllib
import json


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

    url_to_download = git_url + "raw/master/kytos.json"
    testfile = urllib.request.urlopen(url_to_download)
    napp_json = json.loads(str(testfile.read(), encoding="utf-8"))

    author_napps_key = "author:" + login + ":apps"

    if not con.sismember(author_napps_key, napp_json["napp"]["name"]):
        napp_key = "app:" + napp_json["napp"]["name"]

        con.sadd("apps", napp_key)

        # Generate some keys to be added in napp hash
        comments_key = "app:" + napp_json["napp"]["name"] + ":comments"
        ofversions_key = "app:" + napp_json["napp"]["name"] + ":ofversions"
        author_key = "author:" + login
        napp_versions_key = "app:" + napp_json["napp"]["name"] + ":versions"
        napp_tags_key = "app:" + napp_json["napp"]["name"] + ":tags"

        napp_redis_json = {
            "name": napp_json["napp"]["name"],
            "description": napp_json["napp"]["description"],
            "license": napp_json["napp"]["license"],
            "rating": "None",
            "comments": comments_key,
            "ofversions": ofversions_key,
            "author": author_key,
            "tags": napp_tags_key,
            "versions": napp_versions_key
        }
        con.hmset(napp_key, napp_redis_json)

        # Add tags
        for tag in list(napp_json["napp"]["tags"]):
            con.sadd(napp_tags_key, tag)

        # Add version
        for version in list(napp_json["napp"]["version"]):
            con.sadd(napp_versions_key, version)

        # Add ofversion
        for ofversion in list(napp_json["napp"]["ofversion"]):
            con.sadd(ofversions_key, ofversion)

        # Add napp key to the user (author must exist)
        if con.sismember("authors", author_key):
            con.sadd(author_napps_key, napp_key)
        else:
            return 401

        return 200

    else:
        return 401


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
            if len(con.keys(content['token'])) == 0:
                return '', 400
            else:
                author_token_dict = con.hgetall(content['token'])
                current_token = common.Token(token_id=content['token'],
                                     token_exp_time=author_token_dict['expire'],
                                     token_gen_time=author_token_dict['creation'],
                                     token_type="Auth")
                current_user = common.User(login=current_token.token_to_login)
                if current_token.time_to_expire() > 0:
                    ret = napp_git_download(content['git'], current_user.login())
                    return '', ret
                else:
                    return '', 400
        except ValidationError:
            return '', 400
