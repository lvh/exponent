from exponent.auth import common
from twisted.cred import checkers, portal
from twisted.internet import defer
from twisted.protocols import amp
from zope import interface


def _getUserByIdentifier(rootStore, userIdentifier):
    """
    Gets a user by uid.
    """
    user = common.User.findUnique(rootStore, userIdentifier)
    return defer.succeed(user)



class AuthenticationLocator(amp.CommandLocator):
    """
    A base class for responder locators that allow users to authenticate.
    """
    credentialInterfaces = []

    def __init__(self, store):
        """
        Initializes an authentication responder locator.

        :param store: The root store.
        """
        self.store = store

        storeCheckers = store.powerupsFor(checkers.ICredentialsChecker)
        self.portal = portal.Portal(Realm(store), storeCheckers)


    def acquireStore(self, userIdentifier):
        """
        Acquires a user store.
        """



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



def _gotUser(user):
    """
    Adapts the user to ``IBoxReceiver`` and returns a 3-tuple suitable
    as the return value for ``requestAvatar``.
    """
    return amp.IBoxReceiver, amp.IBoxReceiver(user), lambda: None
