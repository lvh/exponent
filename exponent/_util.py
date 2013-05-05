"""
Random utilities that don't fit anywhere else. Internal use only.
"""
from functools import wraps
from twisted.internet import defer


def synchronous(f):
    """
    Makes a synchronous function implementation return a ``Deferred``
    when called, which will either synchronously have its callback
    fired with whatever result the synchronous function returned, or
    have its errback called with whatever exception the synchronous
    function raised.
    """
    @wraps(f)
    def wrapped(*a, **kw):
        return defer.maybeDeferred(f, *a, **kw)

    return wrapped
