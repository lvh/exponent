from axiom import store
from exponent.auth import realm, user
from twisted.cred import portal
from twisted.internet import defer
from twisted.protocols import amp
from twisted.trial import unittest


class RealmTests(unittest.TestCase):
    def test_implements(self):
        """
        Tests that the realm implements the ``IRealm`` interface.
        """
        self.assertTrue(portal.IRealm.implementedBy(realm.Realm))


    def test_badInterface(self):
        """
        Tests that the realm doesn't work without IBoxReceiver as a target
        interface.
        """
        requestAvatar = realm.Realm(None).requestAvatar
        self.assertRaises(NotImplementedError, requestAvatar, "", None, None)


    def test_requestAvatar(self):
        """
        Creates an in-memory user with a stub ``IBoxReceiver``
        powerup, and attempts to request an avatar for that user.
        """
        # TODO: remove store as soon as Axiom supports storeless __conform__
        testUser = user.User(store=store.Store(), uid="test")

        def getUser(uid):
            self.assertEqual(uid, "test")
            return defer.succeed(testUser)

        boxReceiver = object()
        testUser.inMemoryPowerUp(boxReceiver, amp.IBoxReceiver)

        testRealm = realm.Realm(getUser)
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
