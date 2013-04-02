from txampext import errors


class BadCredentials(errors.Error):
    """
    The provided credentials were incorrect.
    """


class DuplicateCredentials(errors.Error):
    """
    The provided credentials have already been taken.
    """
