"""
Tests for the core authentication services.
"""
from axiom import attributes, item, store
from exponent.auth import service, user
from twisted.cred import checkers, credentials, error as ce, portal
from twisted.internet import defer
from twisted.protocols import amp
from twisted.trial import unittest
from zope import interface


class RealmTests(unittest.TestCase):
    def test_implements(self):
        """
        Tests that the realm implements the ``IRealm`` interface.
        """
        self.assertTrue(portal.IRealm.implementedBy(service.Realm))


    def test_badInterface(self):
        """
        Tests that the realm doesn't work without IBoxReceiver as a target
        interface.
        """
        requestAvatar = service.Realm(None).requestAvatar
        self.assertRaises(NotImplementedError, requestAvatar, "", None, None)


    def test_requestAvatar(self):
        """
        Creates an in-memory user with a stub ``IBoxReceiver`` powerup, and
        attempts to request an avatar for that user.
        """
        testUser = user.User(store=store.Store(), uid="test")

        def getUser(uid):
            self.assertEqual(uid, "test")
            return defer.succeed(testUser)

        boxReceiver = object()
        testUser.inMemoryPowerUp(boxReceiver, amp.IBoxReceiver)

        testRealm = service.Realm(getUser)
        d = testRealm.requestAvatar("test", None, amp.IBoxReceiver)

        @d.addCallback
        def checkAvatar(returnValue):
            """
            Checks the return value of ``requestAvatar``.

            Unpacks the value into interface, implementation and logout
            callable. Verifies that the interface is ``IBoxReceiver``, the
            implementation is the in-memory box receiver powerup, and the
            logout callable is a nullary callable.
            """
            interface, implementation, logout = returnValue
            self.assertIdentical(interface, amp.IBoxReceiver)
            self.assertIdentical(implementation, boxReceiver)
            logout()

        return d


class AuthenticationLocatorTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store()
        self.user = user.User(store=store.Store(), uid="uid")
        self.avatar = object()
        self.user.inMemoryPowerUp(self.avatar, amp.IBoxReceiver)


    @defer.inlineCallbacks
    def test_hasWorkingPortal(self):
        """
        Simple test to verify that the superclass produces a working portal.
        """
        checker = _TestChecker()
        self.store.inMemoryPowerUp(checker, checkers.ICredentialsChecker)

        def _getUserByUid(rootStore, uid):
            self.assertIdentical(rootStore, self.store)
            self.assertEqual(uid, "uid")
            return defer.succeed(self.user)

        login = _TestResponder(self.store, _getUserByUid).portal.login
        creds = credentials.UsernamePassword("username", "password")
        iface, avatar, logout = yield login(creds, None, amp.IBoxReceiver)
        self.assertIdentical(iface, amp.IBoxReceiver)
        self.assertIdentical(self.avatar, avatar)
        logout()



class _TestResponder(service.AuthenticationLocator):
    """
    An authentication responder locator for testing.
    """
    credentialInterfaces = [credentials.IUsernamePassword]



@interface.implementer(checkers.ICredentialsChecker)
class _TestChecker(object):
    """
    A ``IUsernamePassword`` checker for testing.
    """
    credentialInterfaces = [credentials.IUsernamePassword]

    def requestAvatarId(self, credentials):
        return "uid"
