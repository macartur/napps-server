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

    authors_dict = {"author": {}}
    authors_names = con.smembers("authors")

    for author_name in authors_names:
        authors_dict["author"][author_name] = con.hgetall(author_name)
        authors_dict["author"][author_name]["apps"] = list(con.smembers
                                                           (con.hget
                                                            (author_name,
                                                             "apps")))

        authors_dict["author"][author_name]["comments"] = list(con.smembers
                                                               (con.hget
                                                                (author_name,
                                                                 "comments")))

    return jsonify(authors_dict)


@user_api.route('/authors/<name>', methods=['GET'])
def get_author(name):

    author_dict = {"author": {}}

    author_dict["author"][name] = con.hgetall(name)
    author_dict["author"][name]["apps"] = list(con.smembers(con.hget
                                                            ("author:"+name,
                                                             "apps")))
    author_dict["author"][name]["comments"] = list(con.smembers
                                                   (con.hget
                                                    ("author:"+name,
                                                        "comments")))
    return jsonify(author_dict)