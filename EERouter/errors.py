"""
Exceptions definitions.
"""


class EEBrightBoxException(Exception):
    """
    Generic exception.
    Deprecated, use EERouterException instead
    """


class EERouterException(EEBrightBoxException):
    """
    Generic exception.
    """


class AuthenticationException(EERouterException):
    """
    Authentication exception.
    """