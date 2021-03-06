from twisted.cred import checkers, portal
from twisted.protocols import amp
from zope import interface


class AuthenticationLocator(amp.CommandLocator):
    """
    A base class for responder locators that allow users to authenticate.
    """
    credentialInterfaces = []

    def __init__(self, rootStore):
        """
        Initializes an authentication responder locator.

        :param rootStore: The root store.
        """
        self.rootStore = rootStore

        storeCheckers = rootStore.powerupsFor(checkers.ICredentialsChecker)
        self.portal = portal.Portal(Realm(rootStore), storeCheckers)



@interface.implementer(portal.IRealm)
class Realm(object):
    """
    A realm that produces box receivers for users.
    """
    def __init__(self, rootStore):
        self.rootStore = rootStore


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
