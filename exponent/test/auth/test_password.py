from axiom import errors as ae, store
from exponent.auth import errors, password, user
from twisted.cred import checkers, credentials, error as ce
from twisted.internet import defer
from twisted.trial import unittest
from zope import interface


class GetUserTests(unittest.TestCase):
    """
    Tests for getting a user by username.
    """
    def setUp(self):
        self.rootStore = store.Store(self.mktemp())
        password._UidUsernameReference(
            store=self.rootStore,
            uid="uid",
            username=u"username")
        userStore = user.User.createChildStore(self.rootStore, "uid")
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
        self.rootStore = store.Store()
        self.userStore = store.Store()
        self.checker = password.CredentialsChecker(store=self.rootStore)
        self.user = user.User(store=self.userStore, uid="uid")

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



class RegisterTests(unittest.TestCase):
    """
    Tests for registration.
    """
    def setUp(self):
        self.locator = password.Locator(store.Store())


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
    credentialInterfaces = [credentials.IUsernameHashedPassword]

    def requestAvatarId(self, credentials, mind):
        if credentials.username == "username":
            return defer.succeed("uid")
        else:
            return defer.fail(ce.UnauthorizedLogin())



class LoginTests(unittest.TestCase):
    """
    Tests for logging in.
    """
    def setUp(self):
        self.store = store.Store()

        checker = password.CredentialsChecker(store=self.store)
        self.store.inMemoryPowerUp(checker, checkers.ICredentialsChecker)

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
