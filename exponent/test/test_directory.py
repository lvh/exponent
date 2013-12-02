"""
Tests for write locks and write lock directories.
"""
from axiom import store
from exponent import directory, exceptions
from twisted.trial import unittest


class LocalWriteLockTests(unittest.TestCase):
    def setUp(self):
        rootStore = store.Store(self.mktemp())
        store.Store(rootStore.filesdir.child("xyzzy"))
        self.directory = directory.LocalWriteLockDirectory(store=rootStore)


    def test_implementsDirectoryInterface(self):
        """
        The directory class implements the ``IWriteLockDirectory`` interface,
        the directory under test provides it.
        """
        IWLD = directory.IWriteLockDirectory
        self.assertTrue(IWLD.implementedBy(directory.LocalWriteLockDirectory))
        self.assertTrue(IWLD.providedBy(self.directory))


    def test_implementsLockInterface(self):
        """The lock class implements the ``IWriteLock`` interface.

        """
        IWL = directory.IWriteLock
        self.assertTrue(IWL.implementedBy(directory.LocalWriteLock))


    def test_acquireWriteAndRelease(self):
        """A user can acquire a lock, then write using it, and then release
        the lock.

        """
        lock = self.successResultOf(self.directory.acquire(["xyzzy"]))
        self.assertTrue(directory.IWriteLock.providedBy(lock))
        self.assertEqual(self.successResultOf(lock.release()), None)


    def test_multipleRelease(self):
        """Attempting to release the same lock multiple times fails.

        """
        lock = self.successResultOf(self.directory.acquire(["xyzzy"]))
        self.assertEqual(self.successResultOf(lock.release()), None)
        failure = self.failureResultOf(lock.release())
        failure.trap(directory.AlreadyReleasedException)


    def test_doesNotExist(self):
        """Attempting to acquire a store that doesn't exist fails.

        """
        d = self.directory.acquire(["DOES", "NOT", "EXIST"])
        self.failureResultOf(d).trap(exceptions.NoSuchStoreException)
