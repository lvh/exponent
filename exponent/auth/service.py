import functools

from exponent.auth import user
from twisted.cred import checkers, portal
from twisted.internet import defer
from twisted.protocols import amp
from zope import interface


def _getUserByUid(rootStore, uid):
    """
    Gets a user by uid.
    """
    return defer.succeed(user.User.findUnique(rootStore, uid))



class AuthenticationResponderLocator(object):
    """
    A base class for responder locators that deal with authentication.
    """
    credentialInterfaces = []

    def __init__(self, store, _getUserByUid=_getUserByUid):
        """
        Initializes an authentication responder locator.

        :param store: The root store.
        :param _getUserByUid: Binary callable that takes a store and a user
        uid, and returns a deferred User. This will be used by the realm to
        get users.
        """
        self.store = store
        realm = Realm(functools.partial(_getUserByUid, store))
        storeCheckers = store.powerupsFor(checkers.ICredentialsChecker)
        self.portal = portal.Portal(realm, storeCheckers)



@interface.implementer(portal.IRealm)
class Realm(object):
    """
    A realm that produces box receivers for users.
    """
    def __init__(self, getUserByUid):
        self._getUser = getUserByUid


    def requestAvatar(self, uid, mind, *interfaces):
        """
        Attempts to get a lock on the user, then adapts it to ``IBoxReceiver``.
        """
        if amp.IBoxReceiver not in interfaces:
            raise NotImplementedError()

        return self._getUser(uid).addCallback(_gotUser)



def _gotUser(thisUser):
    """
    Adapts the user to ``IBoxReceiver`` and returns a 3-tuple suitable
    as the return value for ``requestAvatar``.
    """
    return amp.IBoxReceiver, amp.IBoxReceiver(thisUser), lambda: None
