from axiom import errors as ae, store
from exponent.auth import password, user
from twisted.cred import credentials, error as ce
from twisted.internet import defer
from twisted.trial import unittest
from zope import interface


class GetUserTests(unittest.TestCase):
    """
    Tests for getting a user by username.
    """
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())
        password._UidUsernameReference(store=self.rootStore,
            uid="uid", username=u"username")
        userStore = user.User.createStore(self.rootStore, "uid")
        user.User(store=userStore, uid="uid")


    def _getUser(self, username):
        """
        Like regular ``_getUser``, but with this test case's store partially
        applied.
        """
        return password._getUser(self.rootStore, username)


    def test_getExistingUser(self):
        """
        Attempts to retrieve an existing user by username.
        """
        self.assertEqual(self._getUser(u"username").uid, "uid")


    def test_getNonexistantUser(self):
        """
        Attempts to retrieve a user that doesn't exist.
        """
        self.assertRaises(ae.ItemNotFound, self._getUser, u"BOGUS")



class CredentialsCheckerTests(unittest.TestCase):
    """
    Test cases for the password credentials checker.
    """
    def setUp(self):
        self.store = store.Store()
        self.checker = password.CredentialsChecker(store=self.store)
        self.user = user.User(store=self.store, uid="uid")

        hashedPassword = FakeUsernameHashedPassword("password")
        IUHP = credentials.IUsernameHashedPassword
        self.user.inMemoryPowerUp(hashedPassword, IUHP)


    def _getUser(self, _rootStore, username):
        if username == "username":
            return self.user
        else:
            raise ae.ItemNotFound()


    def _requestAvatarId(self, username, password):
        """
        Requests an avatar id with the given username and password (which
        should be UTF-8 encoded bytestrings).
        """
        loginCredentials = credentials.UsernamePassword(username, password)
        args = loginCredentials, self._getUser
        return defer.maybeDeferred(self.checker.requestAvatarId, *args)


    def test_requestAvatarId(self):
        """
        Requests an avatar id for a user.
        """
        d = self._requestAvatarId("username", "password")
        return d.addCallback(self.assertEqual, self.user.uid)


    def test_requestAvatarIdWithBadPassword(self):
        """
        Requests an avatar id for a user that exists, but with the wrong
        password.
        """
        d = self._requestAvatarId("username", "BOGUS")
        return self.assertFailure(d, ce.UnauthorizedLogin)


    def test_requestAvatarIdForMissingUser(self):
        """
        Requests an avatar id for a missing user.
        """
        d = self._requestAvatarId("BOGUS", "BOGUS")
        return self.assertFailure(d, ce.UnauthorizedLogin)



@interface.implementer(credentials.IUsernameHashedPassword)
class FakeUsernameHashedPassword(object):
    """
    An ``IUsernameHashedPassword`` that actually just does string comparison.
    """
    def __init__(self, password):
        self.password = password


    def checkPassword(self, password):
        return self.password == password
