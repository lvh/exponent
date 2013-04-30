"""
Tests for lock directories.
"""
from axiom import store
from exponent import directory
from twisted.trial import unittest


class NonLockingWriteLockTests(unittest.TestCase):
    def setUp(self):
        rootStore = store.Store(self.mktemp())
        store.Store(rootStore.filesdir.child("xyzzy"))
        self.directory = directory.FakeWriteLockDirectory(store=rootStore)


    def test_implementsDirectoryInterface(self):
        """
        The directory class implements the ``IWriteLockDirectory`` interface,
        the directory under test provides it.
        """
        IWLD = directory.IWriteLockDirectory
        self.assertTrue(IWLD.implementedBy(directory.FakeWriteLockDirectory))
        self.assertTrue(IWLD.providedBy(self.directory))


    def test_implementsLockInterface(self):
        """
        The lock class implements the ``IWriteLock`` interface.
        """
        IWL = directory.IWriteLock
        self.assertTrue(IWL.implementedBy(directory.FakeWriteLock))


    def test_acquireWriteAndRelease(self):
        """
        Attempts to acquire a write lock on a store. Attempts to write using
        the lock, and then finally releases the lock.
        """
        lock = self.successResultOf(self.directory.acquire(["xyzzy"]))
        self.assertTrue(directory.IWriteLock.providedBy(lock))
        self.assertEqual(self.successResultOf(lock.release()), None)


    def test_multipleRelease(self):
        """
        Attempts to release the same lock multiple times.
        """
        lock = self.successResultOf(self.directory.acquire(["xyzzy"]))
        self.assertEqual(self.successResultOf(lock.release()), None)
        failure = self.failureResultOf(lock.release())
        failure.trap(directory.AlreadyReleasedException)


    def test_doesNotExist(self):
        """
        Attempts to acquire a store that doesn't exist.
        """
        d = self.directory.acquire(["DOES", "NOT", "EXIST"])
        self.failureResultOf(d).trap(directory.NoSuchStoreException)
