# System imports
import time

# Third-party imports
from flask import Blueprint
from flask import jsonify

# Local source tree imports
import config

con = config.CON

# Flask Blueprints
api = Blueprint('comments_api', __name__)


def get_redis_list(name, key):
     return list(con.smembers(con.hget(name,key)))


def get_comment(comment_key):
    """
    This routine receives a key for a given comment and returns the JSON with all comment data.
    :param comment_key: The key for the comment
    :return: JSON with structured data of the comment
    """
    return con.hgetall(comment_key)

def get_author(author_key):
    """
    This routine returns a dict with some basic information about the author
    :param author_key:
    :return:
    """
    exclude = ['apps', 'city', 'comments', 'country', 'pass', 'phone', 'role', 'state', 'status', 'timezone', 'tokens']
    author_dict = con.hgetall(author_key)

    for item in exclude:
        author_dict.pop(item, None)

    return author_dict


@api.route('/authors/<name>/comments', methods=['GET'])
def get_author_comments(name):
    """
    This endpoints returns an JSON with all comments of a given application
    """
    user_comments_dict = {}
    comment_number = 0
    user_key = "author:"+name
    if con.sismember("authors", user_key):
        user_comment_key = con.hget(user_key, "comments")
        for comment in list(con.smembers(user_comment_key)):
            user_comments_dict[comment_number] = get_comment(comment)
            author_data = get_author(user_comments_dict[comment_number]["author"])
            user_comments_dict[comment_number]["author"] = author_data
            comment_date = time.strptime(user_comments_dict[comment_number]["datetime"],'%Y%d%m%H%M')
            user_comments_dict[comment_number]["datetime"] = time.strftime("%a, %d %b %Y %H:%M", comment_date)
            comment_number = comment_number + 1
        return jsonify({'comments': user_comments_dict})
    else:
        return None


@api.route('/napps/<name>/comments', methods=['GET'])
def get_napps_comments(name):
    """
    This endpoints returns a JSON with all comments of a given author.
    """
    app_comments_dict = {}
    comment_number = 0
    app_key = "app:"+name
    print(app_key)
    if con.sismember("apps", app_key):
        app_comment_key = con.hget(app_key, "comments")
        for comment in list(con.smembers(app_comment_key)):
            app_comments_dict[comment_number] = get_comment(comment)
            author_data = get_author(app_comments_dict[comment_number]["author"])
            app_comments_dict[comment_number]["author"] = author_data
            comment_date = time.strptime(app_comments_dict[comment_number]["datetime"],'%Y%d%m%H%M')
            app_comments_dict[comment_number]["datetime"] = time.strftime("%a, %d %b %Y %H:%M", comment_date)
            comment_number = comment_number + 1
        return jsonify({'comments': app_comments_dict})
    else:
        return None
