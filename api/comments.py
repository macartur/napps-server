# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify
from flask import request

# Local source tree imports
import config

con = config.CON

# Flask Blueprints
api = Blueprint('comments_api', __name__)


def get_redis_list(name, key):
     return list(con.smembers(con.hget(name,key)))


@api.route('/comments', methods=['GET'])
def get_comments():
    """
    This routine creates an endpoint that shows all comments for each
    application. It returns all information in JSON format.
    """
    comments_dict = {}

    app_indexes = con.smembers("apps")

    for index in app_indexes:
        app_name = con.hget(index,"name")
        for comment in list(con.smembers(index+":comments")):
            comments_dict[app_name] = con.hgetall(comment)

    return jsonify({'comments': comments_dict})


def get_comment(app_name):
    comment_dict = {}
    app_key = "app:"+app_name

    for comment in get_redis_list(app_key, "comments"):
        comment_dict[comment] = con.hgetall(comment)

    return comment_dict
