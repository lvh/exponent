from txampext import errors


class BadCredentials(errors.Error):
    """
    Raised when an operation fails due to bad or missing credentials.
    """
