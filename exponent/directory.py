"""
Lock directories.
"""
from axiom import attributes, item, store
from exponent import exceptions
from twisted.internet import defer
from zope import interface


class IWriteLockDirectory(interface.Interface):
    """
    A write lock directory for stores.
    """
    def acquire(pathSegments):
        """
        Attempts to acquire a write lock on a store.

        :return: Deferred that will fire with the write lock for the requested
            store, or fail with one of the exceptions below.
        :rtype: Deferred ``IWriteLock``
        :raises AlreadyAcquiredException: The requested lock was already
            acquired.
        :raises NoSuchStoreException: The requested store did not exist.
        """



class IWriteLock(interface.Interface):
    """
    A write lock on a store.
    """
    def write(self):
        """
        Writes the store back to permanent storage.
        """


    def release(self):
        """
        Releases the lock on the store.

        :return: A deferred that will fire when the lock has been released.
        :raises AlreadyReleasedException: Raised when the lock was already
            released.
        """



class AlreadyAcquiredException(Exception):
    """
    The requested lock has already been acquired.
    """



class AlreadyReleasedException(Exception):
    """
    The lock that was attempted to be released had already been released.
    """



@interface.implementer(IWriteLockDirectory)
class LocalWriteLockDirectory(item.Item):
    """A local, filesystem-based write lock directory, suitable for a
    single server.

    """
    _dummy = attributes.boolean()

    def acquire(self, pathSegments):
        storePath = self.store.filesdir.descendant(pathSegments)
        if not storePath.exists():
            return defer.fail(exceptions.NoSuchStoreException())
        lock = LocalWriteLock(store.Store(storePath))
        return defer.succeed(lock)



@interface.implementer(IWriteLock)
class LocalWriteLock(object):
    """
    A local write lock.
    """
    def __init__(self, lockedStore):
        self.store = lockedStore
        self.released = False


    def write(self):
        """
        Pretends to write the long-term storage.

        :returns: A deferred fired with C{None}.
        :rtype: deferred ``None``
        """
        return defer.succeed(None)


    def release(self):
        """
        Releases the fake lock.

        :returns: A deferred fired with C{None} or failed with an exception
            noted below.
        :rtype: deferred ``None``
        :raises AlreadyReleasedException: If this lock has been released
            before.
        """
        if self.released:
            return defer.fail(AlreadyReleasedException())

        self.released = True
        return defer.succeed(None)
