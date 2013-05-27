"""
Classic username and password authentication.
"""
from axiom import attributes, item, errors as ae
from exponent import directory
from exponent.auth import errors as eae, service
from twisted.cred import checkers, credentials, error as ce
from twisted.internet import defer
from twisted.protocols import amp
from twisted.python import log
from zope import interface


@interface.implementer(checkers.ICredentialsChecker)
class CredentialsChecker(item.Item):
    """
    Checks the user's username and password.

    This will be stored in the root store.
    """
    credentialInterfaces = [credentials.IUsernamePassword]
    powerupInterfaces = [checkers.ICredentialsChecker]

    _dummy = attributes.boolean()

    def requestAvatarId(self, loginCredentials):
        """
        Attempts to authenticate with the given credentials, producing a
        token.

        :param loginCredentials: The credentials being used to log in: a user
            identifier, and the user identifier's password.
        :type loginCredentials: ``twisted.cred.credentials.IUsernamePassword``
        :returns: A deferred token value, for which there will be a matching
            token in the user's store.
        :rtype: ``Deferred str``
        """
        userIdentifier = loginCredentials.username
        lockDirectory = directory.IWriteLockDirectory(self.store)
        d = lockDirectory.acquire(["users", userIdentifier]).addCallbacks(
            callback=self._userFound, callbackArgs=[loginCredentials],
            errback=self._userNotFound, errbackArgs=[loginCredentials])
        return d


    def _userFound(self, userStore, loginCredentials):
        check = credentials.IUsernameHashedPassword(userStore).checkPassword
        d = defer.maybeDeferred(check, loginCredentials.password)
        return d.addCallback(self._passwordChecked, userStore)


    def _passwordChecked(self, wasCorrect, userStore):
        """
        If the provided password checked out, returns the uid, otherwise raise
        ``UnauthorizedLogin`` and log the failure.
        """
        if wasCorrect:
            return userStore.uid
        else:
            raise ce.UnauthorizedLogin("Wrong password")


    def _userNotFound(self, failure, loginCredentials):
        """
        Logs that the user was not found and raises ``UnauthorizedLogin``.
        """
        failure.trap(ae.ItemNotFound)
        template = "failed password auth, unknown user identifier: {}"
        log.msg(template.format(loginCredentials.username))
        raise ce.UnauthorizedLogin("Unknown user identifier")



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
    errors = dict([eae.BadCredentials.asAMP()])



class AuthenticationLocator(service.AuthenticationLocator):
    """
    A locator for commands related to logging in using a password.
    """
    @AuthenticateWithPassword.responder
    def authenticate(self, userIdentifier, password):
        """
        Attempts to authenticate the user given the password.

        :returns: A deferred authentication token, wrapped in a dictionary
            so it is an appropriate response value.
        :rtype: deferred ``{"token": token}``
        """



class SetPassword(amp.Command):
    """
    Sets the current client's password.
    """
    arguments = [
        ("password", amp.Unicode())
    ]
    response = []
    errors = dict([eae.BadCredentials.asAMP()])



class Locator(amp.CommandLocator):
    """
    A locator for password commands for users that are already logged in.
    """
    def setPassword(self, password):
        """
        Sets the current user's password to the provided value.

        :returns: A deferred that will fire with an empty dictionary when the
            password has been set.
        :rtype: deferred ``{}``
        """
