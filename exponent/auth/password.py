"""
Classic username and password authentication.
"""
from axiom import attributes, item, errors as ae
from exponent.auth import errors as ee, user
from twisted.cred import checkers, credentials, error as ce
from twisted.protocols import amp
from twisted.python import log
from txampext import axiomtypes, exposed
from zope import interface


@interface.implementer(checkers.ICredentialsChecker)
class CredentialsChecker(item.Item):
    """
    Checks the user's username and password.
    """
    credentialInterfaces = [credentials.IUsernamePassword]
    powerupInterfaces = [checkers.ICredentialsChecker]

    def requestAvatarId(self, loginCredentials):
        username = loginCredentials.username.decode("utf-8")
        try:
            thisUser = self._getUserByUsername(username)
        except ae.ItemNotFound:
            log.msg("unknown username: {}".format(loginCredentials.username))
            raise ce.UnauthorizedLogin()

        try:
            storedCredentials = credentials.IUsernameHashedPassword(thisUser)
        except TypeError:  # no stored password
            raise ce.UnauthorizedLogin()

        d = storedCredentials.checkPassword(loginCredentials.password)
        return d.addCallback(lambda _result: user.uid)


    def _getUserByUsername(self, username):
        """
        Gets a user by username.
        """
        UUR = UidUsernameReference
        uid = self.store.findUnique(UUR, UUR.username == username).uid
        return user.User.withUid(self.store, uid)



class UidUsernameReference(item.Item):
    """
    A reference to match a uid to a username.
    """
    uid = attributes.bytes(allowNone=False, indexed=True)
    username = attributes.text(allowNone=False, indexed=True)

    @classmethod
    def forUsername(cls, store, username):
        return store.findUnique(cls, cls.username == username).uid



class RegisterUsernamePassword(amp.Command):
    """
    Registers with a username and password.
    """
    arguments = [
        ("username", amp.Unicode()),
        ("password", amp.Unicode())
    ]
    response = []
    errors = dict([ee.BadCredentials.asAMP()])



class LoginUsernamePassword(amp.Command):
    """
    Log in with a username and password.
    """
    arguments = [
        ("username", amp.Unicode()),
        ("password", amp.Unicode()),
        exposed.EXPOSED_BOX_SENDER
    ]
    response = [
        ("uid", axiomtypes.typeFor(user.User.uid))
    ]
    errors = dict([ee.BadCredentials.asAMP()])



class PasswordAuthenticationLocator(object):
    @LoginUsernamePassword.responder
    def login(self, username, password):
        pass


    @LoginUsernamePassword.responder
    def register(self, username, password):
        pass
