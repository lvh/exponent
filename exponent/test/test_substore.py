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
        segments = ["a", "b", "c"]
        created = substore.createChildStore(self.rootStore, segments)
        retrieved = substore.getChildStore(self.rootStore, segments)

        self.assertNotIdentical(created.dbdir, None)
        self.assertEqual(created.dbdir, retrieved.dbdir)

        for s in [created, retrieved]:
            self.assertEqual(s.parent, self.rootStore)


    def test_getNonexistantSubstore(self):
        """
        Tests that an appropriate error is raised when trying to open a
        substore that doesn't exist.
        """
        getBogus = lambda: substore.getChildStore(self.rootStore, ["BOGUS"])
        self.assertRaises(errors.ItemNotFound, getBogus)



class ChildMixinTests(unittest.TestCase):
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())


    def test_createAndGetSubstore(self):
        created = Child.createChildStore(self.rootStore, ["a", "b", "c"])
        retrieved = Child.getChildStore(self.rootStore, ["a", "b", "c"])
        self.assertEqual(created.dbdir, retrieved.dbdir)

        segs = [Child.typeName, "a", "b", "c"]
        indirectlyRetrieved = substore.getChildStore(self.rootStore, segs)
        self.assertEqual(retrieved.dbdir, indirectlyRetrieved.dbdir)


    def test_findUnique(self):
        childStore = Child.createChildStore(self.rootStore, ["a"])
        createdItem = Child(store=childStore)
        foundItem = Child.findUniqueChild(self.rootStore, ["a"])
        self.assertIdentical(createdItem, foundItem)



class Child(item.Item, substore.ChildMixin):
    _dummy = attributes.boolean()
