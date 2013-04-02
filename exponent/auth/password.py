"""
Classic username and password authentication.
"""
from axiom import attributes, item, errors as ae
from exponent.auth import errors as ee, user, service
from operator import methodcaller
from os import urandom
from twisted.cred import checkers, credentials, error as ce
from twisted.internet import defer
from twisted.protocols import amp
from twisted.python import log
from txampext import axiomtypes, exposed
from zope import interface


def _getUser(rootStore, username):
    """
    Gets a user by username.
    """
    forThisUsername = _UidUsernameReference.username == username
    uid = rootStore.findUnique(_UidUsernameReference, forThisUsername).uid
    return user.User.findUniqueChild(rootStore, uid)



class _UidUsernameReference(item.Item):
    """
    A reference to match a uid to a username.
    """
    uid = attributes.bytes(allowNone=False, indexed=True)
    username = attributes.text(allowNone=False, indexed=True)



@interface.implementer(checkers.ICredentialsChecker)
class CredentialsChecker(item.Item):
    """
    Checks the user's username and password.
    """
    credentialInterfaces = [credentials.IUsernamePassword]
    powerupInterfaces = [checkers.ICredentialsChecker]

    _dummy = attributes.boolean()

    @defer.inlineCallbacks
    def requestAvatarId(self, loginCredentials, _getUser=_getUser):
        username = loginCredentials.username.decode("utf-8")
        try:
            thisUser = yield _getUser(self.store, username)
        except ae.ItemNotFound:
            log.msg("unknown username: {}".format(loginCredentials.username))
            raise ce.UnauthorizedLogin("Unknown username")


        stored = credentials.IUsernameHashedPassword(thisUser)
        isCorrect = yield stored.checkPassword(loginCredentials.password)
        if isCorrect:
            defer.returnValue(thisUser.uid)
        else:
            raise ce.UnauthorizedLogin("Wrong password")



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



class Locator(service.AuthenticationLocator):
    @LoginUsernamePassword.responder
    def login(self, username, password, exposedBoxSender):
        encode = methodcaller("encode", "utf-8")
        username, password = map(encode, [username, password])
        loginCredentials = credentials.UsernamePassword(username, password)

        d = self.portal.login(loginCredentials, None, amp.IBoxReceiver)
        d.addCallbacks(self._loginSucceeded, self._loginFailed)
        return d


    def _loginSucceeded(self, avatar):
        """
        Handles a succeeded login.
        """


    def _loginFailed(self, failure):
        """
        Handles a failed login attempt due to bad credentials.
        """
        failure.trap(ce.UnauthorizedLogin)
        raise ee.BadCredentials()


    @RegisterUsernamePassword.responder
    def register(self, username, password):
        self._checkUnique(username)

        uid = urandom(320 // 8)
        _UidUsernameReference(store=self.store, username=username, uid=uid)
        return {"uid": uid}


    def _checkUnique(self, username):
        """
        Verifies that the given username is unique.
        """
        UUR = _UidUsernameReference
        withThisUsername = UUR.username == username

        references = self.store.query(UUR, withThisUsername, limit=1)
        if references.count() != 0:
            raise ee.DuplicateCredentials()
