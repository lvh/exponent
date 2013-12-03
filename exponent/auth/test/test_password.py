"""
Tests for password-related authentication functionality.
"""
from axiom.store import Store
from exponent.auth import common, password
from exponent.directory import IWriteLockDirectory, LocalWriteLock
from exponent.exceptions import NoSuchStoreException
from exponent._util import synchronous
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import UsernamePassword, IUsernameHashedPassword
from twisted.internet import defer
from twisted.trial.unittest import SynchronousTestCase
from txampext.respondertests import ResponderTestMixin
from zope.interface import implementer


class CredentialsCheckerTests(SynchronousTestCase):
    """
    Test cases for the password credentials checker.
    """
    def setUp(self):
        self.rootStore = Store()
        self.checker = password.CredentialsChecker(store=self.rootStore)

        self.userStore = Store()
        self.user = common.User(store=self.userStore, identifier="uid")

        hashedPassword = FakeUsernameHashedPassword("password")
        self.userStore.inMemoryPowerUp(hashedPassword, IUsernameHashedPassword)

        directory = FakeWriteLockDirectory(self.userStore)
        self.rootStore.inMemoryPowerUp(directory, IWriteLockDirectory)


    def _requestAvatarId(self, username, password):
        """
        Requests an avatar id with the given username and password (which
        should be UTF-8 encoded bytestrings).
        """
        credentials = UsernamePassword(username, password)
        return defer.maybeDeferred(self.checker.requestAvatarId, credentials)


    def test_requestAvatarId(self):
        """
        A user can request an avatar id using a user identifier and password.
        """
        d = self._requestAvatarId("uid", "password")
        uid = self.successResultOf(d)
        self.assertIdentical(uid, "uid")


    def test_requestAvatarIdWithBadPassword(self):
        """
        Requests an avatar id for a user that exists, but with the wrong
        password.
        """
        d = self._requestAvatarId("uid", "BOGUS")
        self.failureResultOf(d, UnauthorizedLogin)


    def test_requestAvatarIdForMissingUser(self):
        """
        Requests an avatar id for a missing user.
        """
        d = self._requestAvatarId("BOGUS", "BOGUS")
        self.failureResultOf(d, UnauthorizedLogin)



@implementer(IWriteLockDirectory)
class FakeWriteLockDirectory(object):
    """
    A fake write lock directory.
    """
    def __init__(self, userStore):
        self.userStore = userStore


    @synchronous
    def acquire(self, pathSegments):
        """Attempts to acquire a user store.

        """
        if pathSegments == ["users", "uid"]:
            return LocalWriteLock(self.userStore)
        else:
            raise NoSuchStoreException()



@implementer(IUsernameHashedPassword)
class FakeUsernameHashedPassword(object):
    """
    An ``IUsernameHashedPassword`` that actually just does string comparison.
    """
    def __init__(self, password):
        self.password = password


    def checkPassword(self, password):
        return self.password == password



class FakeCredentialsChecker(object):
    credentialInterfaces = [IUsernameHashedPassword]

    def requestAvatarId(self, credentials, mind):
        if credentials.username == "username":
            return defer.succeed("uid")
        else:
            return defer.fail(UnauthorizedLogin())



class AuthenticationLocatorTests(SynchronousTestCase, ResponderTestMixin):
    command = password.AuthenticateWithPassword
    locator = password.PasswordAuthenticationLocator(Store())



class PasswordLocatorTests(SynchronousTestCase, ResponderTestMixin):
    command = password.SetPassword
    locator = password.PasswordLocator(Store())
