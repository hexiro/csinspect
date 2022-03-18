"""Custom CS:GO Inspect exception classes"""


class CSGOInspectError(Exception):
    """Base Error class"""


class InvalidInspectLink(CSGOInspectError):
    """Raised when a inspect link was expected, but not provided."""


class InvalidTweetError(CSGOInspectError):
    """Raised when a tweet passed does not posses the data it's supposed to have."""
