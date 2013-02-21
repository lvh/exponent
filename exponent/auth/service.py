"""
A realm that tries to adapt users
"""
from axiom import attributes, item
from twisted.application import service
from twisted.cred import portal
from twisted.cred.checkers import ICredentialsChecker
from twisted.protocols import amp
from zope import interface


@interface.implementer(service.IService)
class AuthenticationService(item.Item):
    _dummy = attributes.inmemory()

    def startService(self):
        realm = Realm()
        checkers = list(self.store.powerupsFor(ICredentialsChecker))
        portal = portal.Portal(realm, checkers)



@interface.implementer(portal.IRealm)
class Realm(object):
    """
    A realm that produces box receivers for users.
    """
    def __init__(self, getUser):
        self._getUser = getUser


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
