"""Module with utilities used into napps-server modules."""
import hashlib
import os

from jinja2 import Template

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(APP_ROOT, 'templates')


def render_template(filename, context):
    """Method used to render the user page."""
    with open(os.path.join(TEMPLATE_DIR, filename), 'r') as f:
        template = Template(f.read())
        return template.render(context)


def generate_hash():
    """Method used to generate a new hash.

    Returns:
        hash (string): String with a hash generated.
    """
    return hashlib.sha256(os.urandom(128)).hexdigest()


def immutableMultiDict_to_dict(schema, immd):
    """Method that converts an ImmutableMultiDict to a dict.

    This convertion consider the expected type of each attribute, based on the
    given schema reference.
    """
    output = dict()
    for key, value in schema.items():
        if key != 'required' and key != 'user':
            if value.get('type') == 'array':
                output[key] = immd.getlist(key)
            else:
                output[key] = immd.get(key)

    for key in immd:
        if key not in output:
            output[key] = immd.get(key)

    return output


def get_request_data(request, schema):
    """Extract the data from a request.

    Check the json, data and form fields in order to get the request data.

    Args:
        request (flask.request): The request that should contain the data
        schema (dict): A dict representing the schema from where the 'json'
            will be structured.
    Return:
        content (dict): A dict ('json') with the data from the request
        None if no data was found.
    """
    content = request.get_json()
    if content is None:
        content = immutableMultiDict_to_dict(schema, request.form)

    return content
