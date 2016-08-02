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


@api.route("/api/register", methods=["POST"])
def author_register():
    """
    This endpoing will be used to add new authors to the system.
    :return: Return HTTP code 200 if user were succesfully registered or 409 (Conflict response code) in others cases.
    """

    content = request.get_json(silent=True)

    try:
        validate(content, common.napp_git_author)
        return '', 200

    except ValidationError:
        return '', 400
