from requests.exceptions import HTTPError


class FreshBooksUnauthenticatedError(HTTPError):
    """A 401 error occured"""

class FreshBooksPaymentRequiredError(HTTPError):
    """A 402 error occured"""
