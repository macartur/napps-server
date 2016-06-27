from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

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
            authors_dict[author_name]['apps'] = get_redis_list(author_name,
                                                               'apps')
            authors_dict[author_name]['comments'] = len(get_redis_list
                                                        (author_name,
                                                         'comments'))
        return jsonify({'authors': authors_dict})


@api.route('/authors/<name>', methods=['GET'])
def get_author(name):
    """
    This routine creates an endpoint that shows details about a specific
    application author. It returns all information in JSON format.
    """
    author = {}
    author_key = "author:"+name
    author[name] = con.hgetall(author_key)
    author[name]["apps"] = get_apps(name)

    return jsonify({'author': author})