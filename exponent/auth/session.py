"""
Session-based authentication.
"""
from axiom import attributes, errors as ae, item
from exponent.auth import common, errors as eae, service
from twisted.protocols import amp


class LoginWithSession(amp.Command):
    """
    Logs in with a session identifier.
    """
    arguments = [
        ("userIdentifier", amp.String()),
        ("sessionIdentifier", amp.String())
    ]
    response = [("sessionIdentifier", amp.String())]



class AuthenticationLocator(service.AuthenticationLocator):
    """
    A locator for logging in using session identifiers.
    """
    def login(self, userIdentifier, sessionIdentifier):
        d = self.acquireStore(userIdentifier)
        return d.addCallback(self._cycleSession)


    def _cycleSession(self, store, sessionIdentifier):
        """
        Verifies the session identifier, invalidates it, and creates a
        new session. Returns the session identifier, wrapped in a dict
        so it is suitable as an AMP response.
        """
        try:
            session = store.findUnique(_Session, identifier=sessionIdentifier)
        except ae.ItemNotFound:
            raise eae.BadCredentials()

        session.deleteFromStore()

        newSession = _Session.create(store)
        return {"sessionIdentifier": newSession.identifier}



class RequestSession(amp.Command):
    """
    Requests a new session identifier.
    """
    arguments = []
    response = [("sessionIdentifier", amp.String())]



class Locator(amp.CommandLocator):
    """
    A locator for session commands for users that are already logged in.
    """
    def requestSession(self):
        """
        Requests a new session.
        """



class _Session(item.Item):
    """
    A stored session.
    """
    identifier = attributes.bytes(allowNone=False)


    @classmethod
    def create(cls, store):
        """
        Creates a session with a random indentifier.
        """
        sessionIdentifier = common._createIdentifier()
        return cls(store=store, identifier=sessionIdentifier)
