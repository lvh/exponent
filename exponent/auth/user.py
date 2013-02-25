"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore


@substore.withSubstores
class User(item.Item):
    """
    A user.
    """
    uid = attributes.bytes(allowNone=False)
