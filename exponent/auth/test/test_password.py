"""
Tests for password-related authentication functionality.
"""
from axiom.store import Store
from exponent.auth import common, errors, password
from exponent.directory import IWriteLockDirectory, LocalWriteLock
from exponent.exceptions import NoSuchStoreException
from exponent._util import synchronous
from twisted.cred.error import UnauthorizedLogin
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import UsernamePassword, IUsernameHashedPassword
from twisted.internet import defer
from twisted.trial.unittest import SynchronousTestCase
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



class _ResponderTestMixin(object):
    command = None
    """
    The command.
    """

    responderName = None
    """
    The name of the responder function.
    """

    def test_locateResponder(self):
        """
        Compares the located responder to the expected responder.
        """
        found = self.locator.locateResponder(self.command.__name__)
        expected = getattr(self.locator, self.responderName).im_func
        self.assertEqual(found, expected)



class RegisterTests(SynchronousTestCase):
    """
    Tests for registration.
    """
    def setUp(self):
        self.locator = password.Locator(Store())


    def register(self, username, password):
        """
        Registers with the given username and password.
        """
        args = username, password
        return defer.maybeDeferred(self.locator.register, *args)


    def test_register(self):
        """
        Try normal registration.
        """
        d = self.register(u"username", u"password")
        return d


    def test_noDuplicateUsernames(self):
        """
        Can't register with a duplicate username.
        """
        d = self.register(u"username", u"password")
        d.addCallback(self._tryToRegisterAgain)
        return d


    def _tryToRegisterAgain(self, _result):
        """
        Attempts to register again using the same username.
        """
        d = self.register(u"username", u"password")
        self.assertFailure(d, errors.DuplicateCredentials)
        return d



class FakeCredentialsChecker(object):
    credentialInterfaces = [IUsernameHashedPassword]

    def requestAvatarId(self, credentials, mind):
        if credentials.username == "username":
            return defer.succeed("uid")
        else:
            return defer.fail(UnauthorizedLogin())



class LoginTests(SynchronousTestCase):
    """
    Tests for logging in.
    """
    def setUp(self):
        self.store = Store()

        checker = password.CredentialsChecker(store=self.store)
        self.store.inMemoryPowerUp(checker, ICredentialsChecker)

        self.locator = password.Locator(self.store)


    def _login(self, username, password):
        """
        Log in.
        """
        args = username, password, None
        return defer.maybeDeferred(self.locator.login, *args)


    def test_success(self):
        """
        Can log in with correct username and password.
        """
        d = self._login(u"username", u"password")
        return d


    def test_badUser(self):
        """
        Can't log in as a user that doesn't exist.
        """
        d = self._login(u"BOGUS", u"BOGUS")
        self.assertFailure(d, errors.BadCredentials)
        return d


    def test_wrongPassword(self):
        """
        Can't log in with wrong password.
        """
        d = self._login(u"username", u"BOGUS")
        self.assertFailure(d, errors.BadCredentials)
        return d
