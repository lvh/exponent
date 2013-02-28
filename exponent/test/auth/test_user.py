from axiom import errors, store
from exponent.auth import user
from twisted.trial import unittest


class UserTests(unittest.TestCase):
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())
        self.uid = "test"
        self.userStore = user.User.createStore(self.rootStore, self.uid)
        self.user = user.User(store=self.userStore, uid=self.uid)


    def test_getUserByUid(self):
        """
        Tests that you can get a user by uid.
        """
        testUser = user.User.findUnique(self.rootStore, "test")
        self.assertEqual(testUser, self.user)
        self.assertEqual(testUser.store, self.userStore)


    def test_getMissingUserByUid(self):
        """
        Tests that you can get an appropriate exception when you try
        to get a user that doesn't exist.
        """
        getBogusUser = lambda: user.User.findUnique(self.rootStore, "bogus")
        self.assertRaises(errors.ItemNotFound, getBogusUser)
