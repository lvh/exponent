"""
Tests for common authentication infrastructure.
"""
from axiom import attributes, errors, item, store
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
        """
        Tests that you can get a user by uid.
        """
        testUser = common.User.findUniqueChild(self.store, ["uid"])
        self.assertEqual(testUser, self.user)
        self.assertEqual(testUser.store, self.user.store)


    def test_getMissingUserByIdentifier(self):
        """
        Tests that you can get an appropriate exception when you try
        to get a user that doesn't exist.
        """
        def getBogusUser():
            return common.User.findUniqueChild(self.store, "BOGUS")
        self.assertRaises(errors.ItemNotFound, getBogusUser)



class CreateUserTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the specification of the ``CreateUser`` command.
    """
    command = common.CreateUser
    argumentObjects = argumentStrings = {}
    responseObjects = responseStrings = {"userIdentifier": "uid"}



class LogInTests(unittest.TestCase, commandtests.CommandTestMixin):
    """
    Tests for the specification of the ``LogIn`` command.
    """
    command = common.LogIn
    argumentObjects = {"tokens": ["a", "b", "c"]}
    argumentStrings = {"tokens": "\x00\x01".join(["", "a", "b", "c"])}
    responseObjects = responseStrings = {}


class CreateIdentifierTests(unittest.TestCase):
    def test_usesSecureEntropySource(self):
        """
        By default, ``_createIdentifier`` uses ``os.urandom``.
        """
        args, _, _, defaults = getargspec(common._createIdentifier)
        defaultEntropySource = defaults[args.index("_urandom")]
        self.assertIdentical(defaultEntropySource, urandom)


    def _createIdentifier(self, **kwargs):
        """
        Creates an identifier with a fake random number generator.
        """
        return common._createIdentifier(_urandom=_urandom, **kwargs)


    def test_default(self):
        """
        By default, ``_createIdentifier`` asks its random number generator for
        a string 320 bits long, and encodes it as hex.
        """
        identifier = self._createIdentifier()
        expectedLength = (320 // 8) * 2 # 320 bits, hex encoded
        self.assertEqual(len(identifier), expectedLength)


    def test_differentNumberOfBits(self):
        """
        ``_createIdentifier`` correctly produces identifiers of different
        length.
        """
        identifier = self._createIdentifier(bits=80)
        expectedLength = (80 // 8) * 2 # 80 bits, hex encoded
        self.assertEqual(len(identifier), expectedLength)



class FakeUrandomTests(unittest.TestCase):
    """
    Tests for the fake, testing-only, ``os.urandom`` stub.
    """
    def test_oneByte(self):
        """
        ``_urandom`` produces ``\x00`` when asked for a single byte.
        """
        self.assertEqual(_urandom(1), "\x00")


    def test_tenBytes(self):
        """
        ``_urandom`` produces 10 NUL bytes when asked for 10 bytes.
        """
        self.assertEqual(_urandom(10), "\x00" * 10)



def _urandom(numBytes):
    """
    Super secure random number generator that returns as many NUL
    bytes as you ask for.
    """
    return "\x00" * numBytes



class TokenSetTests(unittest.TestCase):
    """
    Tests for the token set implementation.
    """
    def test_implementsInterface(self):
        """
        The token set is an ``ICredentials`` as well as an ``ITokenSet``.
        """
        for iface in [common.ITokenSet, credentials.ICredentials]:
            self.assertTrue(iface.implementedBy(common.TokenSet))


    def test_acceptsTokens(self):
        """
        A token set can be instantiated with some tokens. Its identifier
        attribute will be an immutable set of the provided tokens.
        """
        tokenSet = common.TokenSet(["1", "2", "3"])
        self.assertEqual(tokenSet.identifiers, set(["1", "2", "3"]))
        self.assertRaises(AttributeError, lambda: tokenSet.identifiers.add)


    def test_noDuplicateTokenIdentifiers(self):
        """
        A token set can not be instantiated with duplicate tokens.
        """
        self.assertRaises(ValueError, common.TokenSet, ["1", "1", "1"])



class _MagicToken(item.Item):
    """
    A magical token.
    """
    identifier = attributes.bytes()



class _CrazyToken(item.Item):
    """
    A crazy token.
    """
    identifier = attributes.bytes()



class TokenCounterTests(unittest.TestCase):
    """
    Tests for the token-counting credentials checker.
    """
    def setUp(self):
        self.store = store.Store()
        self.user = common.User(store=self.store, identifier="uid")
        self.counter = common.TokenCounter(store=self.store)
        self.token = self._createExtraToken(_MagicToken, "first token")


    def _createExtraToken(self, cls=_CrazyToken, identifier="second token"):
        """
        Creates an extra token of given class and registers it as a powerup.
        """
        extraToken = cls(store=self.store, identifier=identifier)
        self.store.powerUp(extraToken, common.IToken)
        return extraToken


    def test_requireOneTokenByDefault(self):
        """
        By default, the token counter requires one token.
        """
        self.assertEqual(self.counter.requiredTokens, 1)


    def _assertAccepts(self, identifiers):
        """
        Asserts that the counter accepts the given identifiers.
        """
        d = self.counter.requestAvatarId(common.TokenSet(identifiers))
        self.assertEqual(self.successResultOf(d), self.user.identifier)


    def _assertNotAccepts(self, identifiers):
        """
        Asserts that the counter does not accept the given identifiers.
        """
        d = self.counter.requestAvatarId(common.TokenSet(identifiers))
        self.failureResultOf(d).trap(errors.UnauthorizedLogin)


    def test_acceptToken(self):
        """
        The token counter returns the appropriate avatar id when presented
        with a valid token.
        """
        self._assertAccepts([self.token.identifier])
        

    def test_acceptMultipleTokens(self):
        """
        The token counter returns the appropriate avatar id when requiring
        two tokens and being presented with two appropriate tokens.
        """
        self.counter.requiredTokens = 2
        extraToken = self._createExtraToken()
        identifiers = [self.token.identifier, extraToken.identifier]
        self._assertAccepts(identifiers)


    def test_acceptSuperfluousTokens(self):
        """
        The token counter accepts extra tokens, if more were provided than
        are strictly necessary.
        """
        extraToken = self._createExtraToken()
        identifiers = [self.token.identifier, extraToken.identifier]
        self._assertAccepts(identifiers)


    def test_dontAcceptInsufficientTokens(self):
        """
        The token counter does not accept if the number of tokens is
        insufficient.
        """
        self.counter.requiredTokens = 2
        self._assertNotAccepts([self.token.identifier])


    def test_dontAcceptInvalidTokens(self):
        """
        The token counter does not accept invalid tokens.
        """
        self._assertNotAccepts(["BOGUS"])


    def test_dontAcceptDuplicateTokenTypes(self):
        """
        The token counter only accepts a number tokens provided the token
        types are unique.

        Otherwise, an attacker knowing the victim's password could simply
        generate ``N`` password authentication tokens, bypassing a user's
        k-factor auth entirely.
        """
        otherToken = self._createExtraToken(cls=self.token.__class__)
        self._assertNotAccepts([self.token.identifier, otherToken.identifier])










