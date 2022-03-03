from requests.exceptions import HTTPError


class FreshBooksUnauthenticateddError(HTTPError):
    """A 401 error occured"""
