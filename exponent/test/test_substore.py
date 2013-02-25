from axiom import attributes, errors, item, store
from exponent import substore
from twisted.trial import unittest


class SubstoreTests(unittest.TestCase):
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())


    def test_createAndGetSubstore(self):
        """
        Creates a substore and then retrieves it. Asserts that they are both
        stored on the filesystem and in the same place, and that they both
        have the test's root store as a parent.
        """
        segments = "a", "b", "c"
        createdStore = substore.createStore(self.rootStore, segments)
        retrievedStore = substore.getStore(self.rootStore, segments)

        self.assertNotIdentical(createdStore.dbdir, None)
        self.assertEqual(createdStore.dbdir, retrievedStore.dbdir)

        for s in [createdStore, retrievedStore]:
            self.assertEqual(s.parent, self.rootStore)


    def test_getNonexistantSubstore(self):
        """
        Tests that an appropriate error is raised when trying to open a
        substore that doesn't exist.
        """
        getBogus = lambda: substore.getStore(self.rootStore, ["BOGUS"])
        self.assertRaises(errors.ItemNotFound, getBogus)


class WithSubstoreMixinTests(unittest.TestCase):
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())

    def test_createAndGetSubstore(self):
        createdStore = ItemWithSubstore.createStore(self.rootStore, "a", "b", "c")
        gotStore = ItemWithSubstore.getStore(self.rootStore, "a", "b", "c")
        self.assertEqual(createdStore.dbdir, gotStore.dbdir)

        segments = [ItemWithSubstore.typeName, "a", "b", "c"]
        indirectlyGotStore = substore.getStore(self.rootStore, segments)
        self.assertEqual(gotStore.dbdir, indirectlyGotStore.dbdir)


    def test_findUnique(self):
        createdStore = ItemWithSubstore.createStore(self.rootStore, "a")
        createdItem = ItemWithSubstore(store=createdStore)
        foundItem = ItemWithSubstore.findUnique(self.rootStore, "a")
        self.assertIdentical(createdItem, foundItem)



@substore.withSubstores
class ItemWithSubstore(item.Item):
    dummy = attributes.boolean()
