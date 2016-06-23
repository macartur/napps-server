from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

# Flask Blueprints
api = Blueprint('user_api', __name__)
# user_api = Blueprint('user_api', __name__)

con = config.CON

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
    author_dict[name]["apps"] = list(con.smembers(con.hget
                                                  ("author:"+name,"apps")))
    author_dict[name]["comments"] = list(con.smembers
                                         (con.hget("author:"+name,"comments")))

    return jsonify({'author': author_dict})