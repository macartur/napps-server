"""Module with main Exceptions used by napps-server."""


class NappsDuplicateEntry(Exception):
    """Exception thrown when found duplicated napps."""

    pass


class NappsEntryDoesNotExists(Exception):
    """Exception thrown when not found a entry to napp."""

    pass


class InvalidNappMetaData(Exception):
    """Exception thrown when napp have a invalid metadata."""

    pass


class InvalidUser(Exception):
    """Exception thrown when a invalid user is found."""

    pass


class RepositoryNotReachable(Exception):
    """Exception thrown when repository can be found."""

    pass
