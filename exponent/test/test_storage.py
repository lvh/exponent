from axiom import store
from exponent import exceptions, storage
from twisted.trial import unittest


class LocalStorageTests(unittest.TestCase):
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())
        store.Store(self.rootStore.filesdir.child("xyzzy")) # make the store
        self.storage = storage.FakeStorage(store=self.rootStore)


    def test_get(self):
        """
        Local storage retrieves local stores.
        """
        gotStore = self.successResultOf(self.storage.get(["xyzzy"]))
        self.assertEqual(gotStore.dbdir, self.rootStore.filesdir.child("xyzzy"))


    def test_multipleGet(self):
        """
        Requesting the same store sevearl times results in the same store
        object.
        """
        getStore = lambda: self.successResultOf(self.storage.get(["xyzzy"])) 
        self.assertIdentical(getStore(), getStore())


    def test_getNonexistant(self):
        """
        Attemptign to retrieve a nonexistant local store raises
        ``exceptions.NoSuchStoreException``.
        """
        failure = self.failureResultOf(self.storage.get(["BOGUS"]))
        failure.trap(exceptions.NoSuchStoreException)
