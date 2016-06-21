from flask import Blueprint
from flask import jsonify

# Local source tree imports
import config

# Flask Blueprints
users_api = Blueprint('users_api', __name__)
user_api = Blueprint('user_api', __name__)

con = config.CON


@users_api.route('/authors', methods=['GET'])
def get_authors():
    """
    This routine creates an endpoint that shows all applications developers
    (application authors) with their information. It returns all  information
    in JSON format.
    """

    # authors_dict = {"author": {}}
    authors_dict = {}
    authors_names = con.smembers("authors")

    for author_name in authors_names:
        authors_dict[author_name] = con.hgetall(author_name)
        authors_dict[author_name]["apps"] = list(con.smembers
                                                 (con.hget
                                                  (author_name,"apps")))
        # TODO: Put this line in PEP8 format.
        authors_dict[author_name]["comments"] = con.scard(con.hget
                                                          (author_name,"comments"))

    return jsonify({'authors': authors_dict})


@user_api.route('/authors/<name>', methods=['GET'])
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