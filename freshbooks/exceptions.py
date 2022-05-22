from requests.exceptions import HTTPError


class FreshBooksUnauthenticatedError(HTTPError):
    """A 401 error occured"""

class FreshBooksInactiveBusinessError(HTTPError):
    """A 402 error occured"""
