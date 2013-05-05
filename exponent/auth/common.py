"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore
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
