"""
Exceptions raised by napps-server
"""


class TokenExpired(Exception):
    """
    Used when the token is expired and a new authentication is required in order to proceed.
    """

    def __init__(self, token_id):
        """
        The constructor takes an optional message
        :param token_id: Token that generated the exception
        """

        super().__init__()
        self.token_id = token_id

    def __str__(self):
        return 401  # Unauthorized


class TokenDoesNotExist(Exception):
    """
    Used when the token passed by the user,
    """

    def __init__(self, token_id):
        """
        The constructor takes an optional message
        :param token_id: Token that generated the exception
        """

        super().__init__()
        self.token_id = token_id

    def __str__(self):
        return 404  # Resource doesnt exist
