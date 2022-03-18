"""Custom CS:GO Inspect exception classes"""


class CSGOInspectError(Exception):
    """Base Error class"""


class InvalidInspectLink(CSGOInspectError):
    """Raised when a inspect link was expected, but not provided."""
