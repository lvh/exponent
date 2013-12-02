"""
Tests for common authentication infrastructure.
"""
from axiom import errors, scheduler, store
from epsilon import extime
from exponent.auth import common
from inspect import getargspec
from os import urandom
from twisted.cred import credentials
from twisted.trial import unittest
from txampext import commandtests


class UserTests(unittest.TestCase):
    def setUp(self):
        self.store = store.Store(self.mktemp())
        userStore = common.User.createChildStore(self.store, ["uid"])
        self.user = common.User(store=userStore, identifier="uid")


    def test_getUserByIdentifier(self):
        """A user can be found by user identifier.

        """
        testUser = common.User.findUniqueChild(self.store, ["uid"])
        self.assertEqual(testUser, self.user)
        self.assertEqual(testUser.store, self.user.store)


    def test_getMissingUserByIdentifier(self):
        """When trying to get a user that doesn't exist, an exception is
        raised.

        """
        self.assertRaises(errors.ItemNotFound,
                          common.User.findUniqueChild, self.store, "BOGUS")



class CreateUserTests(unittest.TestCase, commandtests.CommandTestMixin):
    """Tests for the specification of the ``CreateUser`` command.

    """
    command = common.CreateUser
    argumentObjects = argumentStrings = {}
    responseObjects = responseStrings = {"userIdentifier": "uid"}
    errors = fatalErrors = {}



class LogInTests(unittest.TestCase, commandtests.CommandTestMixin):
    """Tests for the specification of the ``LogIn`` command.

    """
    command = common.LogIn
    argumentObjects = {"tokens": ["a", "b", "c"]}
    argumentStrings = {"tokens": "\x00\x01".join(["", "a", "b", "c"])}
    responseObjects = responseStrings = {}
    errors = fatalErrors = {}



class CreateIdentifierTests(unittest.TestCase):
    def test_usesSecureEntropySource(self):
        """By default, ``_createIdentifier`` uses ``os.urandom``.

        """
        args, _, _, defaults = getargspec(common._createIdentifier)
        defaultEntropySource = defaults[args.index("_urandom")]
        self.assertIdentical(defaultEntropySource, urandom)


    def _createIdentifier(self, **kwargs):
        """Creates an identifier with a fake random number generator.

        """
        return common._createIdentifier(_urandom=_urandom, **kwargs)


    def test_default(self):
        """By default, ``_createIdentifier`` asks its random number generator
        for a string 160 bits long, and encodes it as hex.

        """
        identifier = self._createIdentifier()
        expectedLength = (160 // 8) * 2 # 160 bits, hex encoded
        self.assertEqual(len(identifier), expectedLength)


    def test_differentNumberOfBits(self):
        """``_createIdentifier`` correctly produces identifiers of different
        length.

        """
        identifier = self._createIdentifier(bits=80)
        expectedLength = (80 // 8) * 2 # 80 bits, hex encoded
        self.assertEqual(len(identifier), expectedLength)



class FakeUrandomTests(unittest.TestCase):
    """Tests for the ``_urandom`` fake.

    """
    def test_oneByte(self):
        """Fake ``_urandom`` produces ``\x00`` when asked for a single byte.

        """
        self.assertEqual(_urandom(1), "\x00")


    def test_tenBytes(self):
        """Fake ``_urandom`` produces 10 NUL bytes when asked for 10 bytes.

        """
        self.assertEqual(_urandom(10), "\x00" * 10)



def _urandom(numBytes):
    """Super secure random number generator that returns as many NUL
    bytes as you ask for.

    """
    return "\x00" * numBytes



class TokenInvalidationTests(unittest.TestCase):
    """Tests for automatic time-based token invalidation.

    """
    def setUp(self):
        self.now = extime.Time()
        self.store = store.Store()
        self.scheduler = scheduler.IScheduler(self.store)
        self.scheduler.now = lambda: self.now


    def test_oneMinute(self):
        """Tokens are valid for one minute.

        """
        self.assertEqual(common.Token.validity.total_seconds(), 60)


    def test_invalidate(self):
        """A token is removed from the store when the validity period has
        passed.

        """
        token = common.Token(store=self.store, source="test")
        self.now = extime.Time() + token.validity
        self.scheduler.tick()
        self.assertIdentical(token.store, None)


    def test_invalidateWhenAlreadyDeletedFromStore(self):
        """The invalidator completes cleanly if the token was already deleted
        from the store.

        """
        token = common.Token(store=self.store, source="test")
        token.deleteFromStore()
        self.now = extime.Time() + token.validity
        self.scheduler.tick()



class TokenTests(object):
    """Tests for token implementations.

    """
    tokenClass = None

    def test_usesRandomIdentifier(self):
        """The token identifier is created by the function that produces
        identifiers.

        """
        factory = common.Token.identifier.defaultFactory
        self.assertIdentical(factory, common._createIdentifier)


    def test_interface(self):
        """Tokens provide the ``IToken`` interface.

        """
        self.assertTrue(common.IToken.providedBy(common.Token()))



class TokenSetTests(unittest.TestCase):
    """Tests for the token set implementation.

    """
    def test_implementsInterface(self):
        """The token set is an ``ICredentials`` as well as an ``ITokenSet``.

        """
        for iface in [common.ITokenSet, credentials.ICredentials]:
            self.assertTrue(iface.implementedBy(common.TokenSet))


    def test_acceptsTokens(self):
        """A token set can be instantiated with some tokens. Its identifier
        attribute will be an immutable set of the provided tokens.

        """
        tokenSet = common.TokenSet(["1", "2", "3"])
        self.assertEqual(tokenSet.identifiers, set(["1", "2", "3"]))
        self.assertRaises(AttributeError, lambda: tokenSet.identifiers.add)


    def test_noDuplicateTokenIdentifiers(self):
        """A token set can not be instantiated with duplicate tokens.

        """
        self.assertRaises(ValueError, common.TokenSet, ["1", "1", "1"])



class TokenCounterTests(unittest.TestCase):
    """Tests for the token-counting credentials checker.

    """
    def setUp(self):
        self.store = store.Store()
        self.user = common.User(store=self.store, identifier="uid")
        self.counter = common.TokenCounter(store=self.store)
        self.token = common.Token(store=self.store, source="magic")


    def test_requireOneTokenByDefault(self):
        """By default, the token counter requires one token.

        """
        self.assertEqual(self.counter.requiredTokens, 1)


    def _assertAccepts(self, identifiers):
        """Asserts that the counter accepts the given identifiers.
        Furthermore, asserts that the identifiers are invalidated
        after being accepted.

        """
        d = self.counter.requestAvatarId(common.TokenSet(identifiers))
        self.assertEqual(self.successResultOf(d), self.user.identifier)


    def _assertNotAccepts(self, identifiers):
        """Asserts that the counter does not accept the given identifiers.
        Furthermore, asserts that the identifiers are not invalidated
        after being rejected.

        """
        d = self.counter.requestAvatarId(common.TokenSet(identifiers))
        self.failureResultOf(d).trap(errors.UnauthorizedLogin)


    def _countTokens(self, identifiers):
        """Counts the number of tokens in the store that have one of the
        given identifiers.

        """
        withIdentifier = common.Token.identifier.oneOf(identifiers)
        return self.store.query(common.Token, withIdentifier).count()


    def test_acceptToken(self):
        """The token counter returns the appropriate avatar id when presented
        with a valid token.

        """
        self._assertAccepts([self.token.identifier])


    def test_acceptMultipleTokens(self):
        """The token counter returns the appropriate avatar id when requiring
        two tokens and being presented with two appropriate tokens.

        """
        extraToken = common.Token(store=self.store, source="guesswork")
        self.assertNotEqual(extraToken.source, self.token.source)
        identifiers = [self.token.identifier, extraToken.identifier]

        self.counter.requiredTokens = 2
        self._assertAccepts(identifiers)


    def test_acceptSuperfluousTokens(self):
        """The token counter accepts extra tokens, if more were provided than
        are strictly necessary.

        """
        extraToken = common.Token(store=self.store, source="guesswork")
        identifiers = [self.token.identifier, extraToken.identifier]
        self._assertAccepts(identifiers)


    def test_dontAcceptInsufficientTokens(self):
        """The token counter does not accept if the number of tokens is
        insufficient.

        """
        self.counter.requiredTokens = 2
        self._assertNotAccepts([self.token.identifier])


    def test_dontAcceptInvalidTokens(self):
        """The token counter does not accept invalid token identifiers.

        """
        self._assertNotAccepts(["BOGUS"])


    def test_dontAcceptDuplicateTokenTypes(self):
        """The token counter only accepts a number tokens provided the token
        sources are unique.

        Otherwise, an attacker that can satisfy one authentication
        mechanism (for example: a user's password) could simply
        generate ``N`` password authentication tokens, bypassing a
        user's k-factor auth entirely.

        """
        otherToken = common.Token(store=self.store, source=self.token.source)
        self._assertNotAccepts([self.token.identifier, otherToken.identifier])
