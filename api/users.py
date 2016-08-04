# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request
from jsonschema import validate
from jsonschema import ValidationError

# Local source tree imports
import config
from api import common


# Flask Blueprints
api = Blueprint('user_api', __name__)

con = config.CON


def get_apps(author_name):
    exclude = ['author', 'tags', 'comments', 'license', 'description']

    author_napps = {}
    author_key = "author:"+author_name
    for apps in get_redis_list(author_key,'apps'):
        author_napps[apps] = con.hgetall('app:'+apps)
        author_napps[apps]['ofversions'] = get_redis_list(apps,"ofversions")
        author_napps[apps]['versions'] = get_redis_list(apps,"versions")
        for item in exclude:
            author_napps[apps].pop(item, None)
    return author_napps


def add_user(author_json):

    author_key = "author:"+ author_json["login"]

    if not con.sismember("authors", author_key):
        author_apps_key = author_key + ":apps"
        author_comment_key = author_key + ":comments"
        author_token_key = author_key + ":tokens"

        author_json = {
            "login": author_json["login"],
            "name": author_json["name"],
            "pass": common.hash_pass(author_json["pass"]),
            "email": author_json["email"],
            "phone": author_json["phone"],
            "city": author_json["city"],
            "state": author_json["state"],
            "country": author_json["country"],
            "timezone": author_json["timezone"],
            "apps": author_apps_key,
            "comments": author_comment_key,
            "token": author_token_key,
            "status": "inactive"
        }
        con.sadd("authors", author_key)
        con.hmset(author_key, author_json)
        return True
    else:
        return False


def get_redis_list(name, key):
     return list(con.smembers(con.hget(name,key)))


@api.route('/api/authors', methods=['GET'])
def get_authors():
    """
    This routine creates an endpoint that shows all applications developers
    (application authors) with their information. It returns all  information
    in JSON format.
    """

    authors = {}
    authors_names = con.smembers("authors")

    for name in authors_names:
        author = con.hgetall(name)
        author["apps"] = get_redis_list(name, 'apps')
        author["comments"] = len(get_redis_list(name, 'comments'))
        authors[name] = author

    return jsonify({'authors': authors})


@api.route('/api/authors/<name>', methods=['GET'])
def get_author(name):
    """
    This routine creates an endpoint that shows details about a specific
    application author. It returns all information in JSON format.
    """
    author_key = "author:"+name
    author = con.hgetall(author_key)
    author["apps"] = get_apps(name)
    author["comments"] = len(get_redis_list(name, 'comments'))

    return jsonify({'author': author})


@api.route("/api/authors/register", methods=["POST"])
def author_register():
    """
    This endpoing will be used to add new authors to the system.
    :return: Return HTTP code 200 if user were succesfully registered or 409 (Conflict response code) in others cases.
    """

    content = request.get_json(silent=True)

    try:
        validate(content, common.napp_git_author)
        if add_user(content):
            return '', 200
        else:
            return '', 409

    except ValidationError:
        return '', 400
