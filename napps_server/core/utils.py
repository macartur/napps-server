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
