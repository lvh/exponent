"""
Tests for common authentication infrastructure.
"""
from axiom import errors, store
from exponent.auth import common
from twisted.trial import unittest
from txampext import commandtests


class UserTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store(self.mktemp())
        userStore = common.User.createChildStore(self.store, ["uid"])
        self.user = common.User(store=userStore, identifier="uid")


    def test_getUserByIdentifier(self):
        """
        Tests that you can get a user by uid.
        """
        testUser = common.User.findUniqueChild(self.store, ["uid"])
        self.assertEqual(testUser, self.user)
        self.assertEqual(testUser.store, self.user.store)


    def test_getMissingUserByIdentifier(self):
        """
        Tests that you can get an appropriate exception when you try
        to get a user that doesn't exist.
        """
        def getBogusUser():
            return common.User.findUniqueChild(self.store, "BOGUS")
        self.assertRaises(errors.ItemNotFound, getBogusUser)



class CreateUserTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the specification of the ``CreateUser`` command.
    """
    command = common.CreateUser
    argumentObjects = argumentStrings = {}
    responseObjects = responseStrings = {"userIdentifier": "uid"}



class LogInTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the specification of the ``LogIn`` command.
    """
    command = common.LogIn
    argumentObjects = {"tokens": ["a", "b", "c"]}
    argumentStrings = {"tokens": "\x00\x01".join(["", "a", "b", "c"])}
    responseObjects = responseStrings = {}
