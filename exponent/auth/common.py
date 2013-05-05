"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore
from os import urandom
from twisted.protocols import amp


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
