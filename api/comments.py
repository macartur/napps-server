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


@api.route('/comments', methods=['GET'])
def get_comments():
    """
    This routine creates an endpoint that shows all comments for each
    application. It returns all information in JSON format.
    """

    if 'name' in request.args:
        return get_comment(request.args['name'])

    else:
        comments_dict = {}
        app_indexes = con.smembers("apps")

        for index in app_indexes:
            app_name = con.hget(index,"name")
            for comment in list(con.smembers(index+":comments")):
                comments_dict[comment] = con.hgetall(comment)

    return jsonify({'comments': comments_dict})


