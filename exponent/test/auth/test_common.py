"""
Tests for common authentication infrastructure.
"""
from axiom import errors, store
from exponent.auth import common
from inspect import getargspec
from os import urandom
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
