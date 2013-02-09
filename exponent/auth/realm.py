"""
A realm that tries to adapt users
"""
from twisted.cred import portal
from twisted.protocols import amp
from zope import interface


@interface.implementer(portal.IRealm)
class Realm(object):
    """
    The realm for the IGL API.
    """
    interface.implements(portal.IRealm)

    def __init__(self, getUser):
        self._getUser = getUser


    def requestAvatar(self, uid, mind, *interfaces):
        """
        Create IGL API avatars for any IBoxReceiver request.
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
