from axiom import errors as ae, store
from exponent.auth import password, user
from twisted.cred import credentials, error as ce
from twisted.internet import defer
from twisted.trial import unittest
from zope import interface


class CredentialsCheckerTests(unittest.TestCase):
    """
    Test cases for the password credentials checker.
    """
    def setUp(self):
        self.checker = password.CredentialsChecker()
        self.user = user.User(store=store.Store(), uid="uid")

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
