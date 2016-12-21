"""Module used to handle comments from napps."""
# System imports
import time

# Third-party imports
from flask import Blueprint, jsonify

# Local source tree imports
from napps_server import config

con = config.CON

# Flask Blueprints
api = Blueprint('comments_api', __name__)


def get_redis_list(name, key):
    """Method used to get all members of a given name and key.

    This method get a name and a key, builds a hash and get all values stored
    by redis using that hash.

    Parameters:
        name (string): name to be searchable by redis.
        key (string): key value to be searchable by redis

    Returns:
        redis_list (list): list with all members of a given name and key.
    """
    return list(con.smembers(con.hget(name, key)))


def get_comment(comment_key):
    """Get a json with all comment data using a key from a given comment.

    Parameters:
        comment_key (string): The key from a comment.
    Returns:
        json (string): JSON with structured data of the comment.
    """
    return con.hgetall(comment_key)


def get_author(author_key):
    """Get a python dictionary with some basic informations about the author.

    Parameters:
        author_key (string): The key from a author.
    Returns:
        author (dict): python dictonary with author informations.
    """
    exclude = ['apps', 'city', 'comments', 'country', 'pass', 'phone', 'role',
               'state', 'status', 'timezone', 'tokens']
    author_dict = con.hgetall(author_key)

    for item in exclude:
        author_dict.pop(item, None)

    return author_dict


@api.route('/authors/<name>/comments', methods=['GET'])
def get_author_comments(name):
    """Method used to get all comments of a given author.

    This method creates a '/authors/<name>/comments' endpoint to return a JSON
    with all comments of a given author.

    Parameters:
        name (string): Name of a author.
    Returns:
        json (string): Structured JSON with a list of comments.
    """
    user_key = "author:" + name
    if con.sismember("authors", user_key):
        return get_all_comments(user_key)


@api.route('/napps/<name>/comments', methods=['GET'])
def get_napps_comments(name):
    """Method used to get all comments of a given Network Application.

    This method creates a '/napps/<name>/comments' endpoint to return a JSON
    with all comments of a given Network Application.

    Parameters:
        name (string): Name of Network Application.
    Returns:
        json (string): Structured JSON with all comments.
    """
    app_key = "app:" + name
    if con.sismember("apps", app_key):
        return get_all_comments(app_key)


def get_all_comments(key):
    """Method used to get all comments of a given key.

    Parameters:
        key (string): String key stored by redis.
    Returns:
        json (string): JSON Structured with all comments of a given key.
    """
    comments_dict = {}
    comment_number = 0
    for comment_key in get_redis_list(key, "comments"):
        comment = get_comment(comment_key)
        comments_dict[comment_number] = comment

        author_data = get_author(comment["author"])
        comments_dict[comment_number]["author"] = author_data

        comment_date = format_comment(comment["datetime"])
        comments_dict[comment_number]["datetime"] = comment_date

        comment_number += 1

    return jsonify({'comments': comments_dict})


def format_comment(date):
    """Method used to format a datetime to comment date format.

    Parameters:
        date (datetime.datetime): A python datetime structure.
    Returns:
        comment_date (string): A string with comment date format.
    """
    comment_date = time.strptime(date, '%Y%d%m%H%M')
    return time.strftime("%a, %d %b %Y %H:%M", comment_date)
