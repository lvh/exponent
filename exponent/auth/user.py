"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore


class User(item.Item, substore.ChildMixin):
    """
    A user.
    """
    uid = attributes.bytes(allowNone=False)
