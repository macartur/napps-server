from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

# Flask Blueprints
api = Blueprint('user_api', __name__)
# user_api = Blueprint('user_api', __name__)

con = config.CON


def get_apps(author_name):
    exclude = ['author', 'tags', 'comments', 'license']

    author_napps = {}
    for apps in list(con.smembers(con.hget(author_name,"apps"))):
        author_napps[apps] = con.hgetall("app:"+apps)
        for item in exclude:
            author_napps.pop(item, None)

    return author_napps


def get_redis_list(name, key):
    return list(con.smembers(con.hget(name,key)))


@api.route('/authors', methods=['GET'])
def get_authors():
    """
    This routine creates an endpoint that shows all applications developers
    (application authors) with their information. It returns all  information
    in JSON format.
    """

    authors_dict = {}
    authors_names = con.smembers("authors")

    if 'name' in request.args:
        return get_author(request.args['name'])
    else:
        for author_name in authors_names:
            authors_dict[author_name] = con.hgetall(author_name)
            authors_dict[author_name]["apps"] = list(con.smembers
                                                     (con.hget
                                                      (author_name,"apps")))
            authors_dict[author_name]["comments"] = con.scard(con.hget
                                                              (author_name,
                                                               "comments"))
        return jsonify({'authors': authors_dict})


@api.route('/authors/<name>', methods=['GET'])
def get_author(name):
    """
    This routine creates an endpoint that shows details about a specific
    application author. It returns all information in JSON format.
    """

    author_dict = {}

    author_dict[name] = con.hgetall(name)
    author_dict[name]["apps"] = get_apps(name)

    # author_dict[name] = con.hgetall(name)
    # author_dict[name]["apps"] = list(con.smembers(con.hget
    #                                               ("author:"+name,"apps")))
    # author_dict[name]["comments"] = list(con.smembers
    #                                      (con.hget("author:"+name,"comments")))

    return jsonify({'author': author_dict})