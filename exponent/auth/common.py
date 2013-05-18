"""
The base model for users.
"""
from axiom import attributes, item, scheduler
from datetime import timedelta
from epsilon import extime
from exponent import substore, _util
from os import urandom
from twisted.cred import checkers, credentials, error
from twisted.protocols import amp
from zope import interface


class User(item.Item, substore.ChildMixin):
    """
    A user.
    """
    identifier = attributes.bytes(allowNone=False)



class CreateUser(amp.Command):
    """
    Creates a new user.
    """
    arguments = []
    response = [("userIdentifier", amp.String())]



class LogIn(amp.Command):
    """
    Logs in, using a number of previously acquired tokens.
    """
    arguments = [("tokens", amp.ListOf(amp.String()))]
    response = []



def _createIdentifier(bits=320, _urandom=urandom):
    """
    Creates a random identifier with ``bits`` worth of entropy, and encodes it
    as a hexadecimal number.

    :param bits: The number of bits of entropy.
    :type bits: ``int``
    :param _urandom: Random bytes generator.
    :type _urandom: unary callable, num_bytes -> bytes
    :return: A hexadecimal identifier with ``bits`` worth of entropy.
    :rtype: bytes
    """
    return urandom(bits // 8).encode("hex")



class IToken(interface.Interface):
    """
    A temporary authentication token.
    """
    identifier = interface.Attribute(
        """
        The token identifier.
        """)



class _InvalidationMixin(object):
    """
    A mixin for tokens that invalidates them after some amount of time.
    """
    validity = timedelta(seconds=60)
    """
    The amount of time to wait before automatically removing the token.
    """


    def stored(self):
        """
        Schedules the token to be invalidated.
        """
        invalidator = _TokenInvalidator(store=self.store, token=self)
        when = extime.Time() + self.validity
        scheduler.IScheduler(self.store).schedule(invalidator, when)



class _TokenInvalidator(item.Item):
    """
    When run, invalidates a token by deleting it from the store.
    """
    token = attributes.reference(allowNone=False)

    def run(self):
        """
        Deletes the token from the store, if it still exists.
        """
        if self.token is not None:
            self.token.deleteFromStore()



@interface.implementer(IToken)
class Token(_InvalidationMixin, item.Item):
    """
    A generic token.
    """
    identifier = attributes.bytes(defaultFactory=_createIdentifier)



class ITokenSet(credentials.ICredentials):
    """
    A set of tokens identifiers being used to log in.
    """
    identifiers = interface.Attribute(
         """
         The set of token identifiers in this login attempt.

         :type: ``frozenset``
         """)



@interface.implementer(ITokenSet)
class TokenSet(object):
    """
    A set of token identifiers.

    These are credentials being used to log in.
    """
    def __init__(self, identifiers):
        self.identifiers = frozenset(identifiers)
        if len(self.identifiers) != len(identifiers):
            raise ValueError("Duplicate token identifiers")



@interface.implementer(checkers.ICredentialsChecker)
class TokenCounter(item.Item):
    """
    A token set checker that accepts a certain number (or more) valid
    tokens of a unique type.

    The simplest (and also default) behavior for this class is a
    number of required tokens of 1 -- that is, any authentication
    token will be accepted.

    The second simplest is a number of required tokens of 0, meaning no
    authentication at all is required to log in as anyone.

    This should be stored in the user's store.
    """
    credentialInterfaces = [ITokenSet]

    requiredTokens = attributes.integer(allowNone=False, default=1)

    @_util.synchronous
    def requestAvatarId(self, credentials, mind=None):
        identifiers, types = set(), set()
        for token in self.store.powerupsFor(IToken):
            identifiers.add(token.identifier)
            if type(token) in types:
                raise error.UnauthorizedLogin()
            else:
                types.add(type(token))

        if len(identifiers & credentials.identifiers) >= self.requiredTokens:
            return self.store.findUnique(User).identifier
        else:
            raise error.UnauthorizedLogin()
