# System imports

# Third-party imports

# Local source tree imports

# JSON Schema for Napps
napps_schema = {
    "git": {"type": "string"},
    "token":  {"type": "string"},
    "required": ["git", "token"]}

# JSON Schema for authentication
napps_auth = {
    "login": {"type": "string"},
    "password": {"type": "string"},
    "required": ["login", "password"]}

# JSON Schema for Napps Description
napp_git_schema = {
    "napp": {
            "name": {"type": "string"},
            "version": {"type": "string"},
            "ofversion": {"type": "string"},
            "dependencies": {"type": "string"},
            "description": {"type": "string"},
            "license": {"type": "string"},
            "git": {"type": "string"},
            "tags": {"type": "array"},
            "required": ["name", "version", "ofversion", "license"]
    },
    "required": ["napp"]
}

# JSON Schema to Add New Authors

