"""
Classic username and password authentication.
"""
from axiom import attributes, item
from exponent import directory, exceptions, locators
from exponent.auth.errors import BadCredentials
from exponent.auth.service import AuthenticationLocator
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred.credentials import IUsernameHashedPassword, IUsernamePassword
from twisted.cred.error import UnauthorizedLogin
from twisted.internet import defer
from twisted.protocols import amp
from twisted.python import log
from zope import interface


@interface.implementer(ICredentialsChecker)
class CredentialsChecker(item.Item):
    """
    Checks the user's user identifier and password.

    This will be stored in the root store.
    """
    credentialInterfaces = [IUsernamePassword]
    powerupInterfaces = [ICredentialsChecker]

    _dummy = attributes.boolean()

    @defer.inlineCallbacks
    def requestAvatarId(self, loginCredentials):
        """
        Attempts to authenticate with the given credentials, producing a
        token.

        :param loginCredentials: The credentials being used to log in: a user
            identifier, and the user's password.
        :type loginCredentials: ``twisted.cred.credentials.IUsernamePassword``
        :returns: A deferred token value, for which there will be a matching
            token in the user's store.
        :rtype: ``Deferred str``
        """
        identifier = loginCredentials.username
        lockDirectory = directory.IWriteLockDirectory(self.store)
        try:
            lock = yield lockDirectory.acquire(["users", identifier])
        except directory.AlreadyAcquiredException:
            pass # TODO: do something useful here
        except exceptions.NoSuchStoreException:
            log.msg("unknown user identifier: {0}".format(identifier))
            raise UnauthorizedLogin("Unknown user identifier")

        storedCredentials = IUsernameHashedPassword(lock.store)
        if (yield storedCredentials.checkPassword(loginCredentials.password)):
            defer.returnValue(identifier)
        else:
            raise UnauthorizedLogin("Wrong password")



class AuthenticateWithPassword(amp.Command):
    """
    Authenticates with a password.
    """
    arguments = [
        ("userIdentifier", amp.String()),
        ("password", amp.Unicode())
    ]
    response = [
        ("token", amp.String()),
    ]
    errors = dict([BadCredentials.asAMP()])



class PasswordAuthenticationLocator(AuthenticationLocator):
    """A locator for commands related to logging in using a password.

    """
    @AuthenticateWithPassword.responder
    def authenticate(self, userIdentifier, password):
        """Attempts to authenticate the user given the password.

        :returns: A deferred authentication token, wrapped in a dictionary
            so it is an appropriate response value.
        :rtype: deferred ``{"token": token}``

        """
        raise NotImplementedError()



class SetPassword(amp.Command):
    """Sets the current client's password.

    """
    arguments = [
        ("password", amp.Unicode())
    ]
    response = []
    errors = dict([BadCredentials.asAMP()])



class PasswordLocator(locators.Locator):
    """A locator for password commands for logged-in users.

    """
    @SetPassword.responder
    def setPassword(self, password):
        """Sets the current user's password to the given value.

        :returns: A deferred that will fire with an empty dictionary when the
            password has been set.
        :rtype: deferred ``{}``

        """
        raise NotImplementedError()
