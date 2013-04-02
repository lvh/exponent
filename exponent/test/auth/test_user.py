from axiom import errors, store
from exponent.auth import user
from twisted.trial import unittest


class UserTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store(self.mktemp())
        self.uid = "test"
        userStore = user.User.createChildStore(self.store, [self.uid])
        self.user = user.User(store=userStore, uid=self.uid)


    def test_getUserByUid(self):
        """
        Tests that you can get a user by uid.
        """
        testUser = user.User.findUniqueChild(self.store, ["test"])
        self.assertEqual(testUser, self.user)
        self.assertEqual(testUser.store, self.user.store)


    def test_getMissingUserByUid(self):
        """
        Tests that you can get an appropriate exception when you try
        to get a user that doesn't exist.
        """
        def getBogusUser():
            return user.User.findUniqueChild(self.store, "BOGUS")
        self.assertRaises(errors.ItemNotFound, getBogusUser)
