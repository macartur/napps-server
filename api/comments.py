# System imports

# Third-party imports
from flask import Blueprint
from flask import jsonify

# Local source tree imports
import config

con = config.CON

# Flask Blueprints
comments_api = Blueprint('comments_api', __name__)


@comments_api.route('/comments', methods=['GET'])
def get_comments():

    comments_dict = {"comments": {}}
    app_indexes = con.smembers("apps")

    for index in app_indexes:
        app_name = con.hget(index,"name")
        for comment in list(con.smembers(index+":comments")):
            comments_dict["comments"][comment] = con.hgetall(comment)

    return jsonify(comments_dict)
