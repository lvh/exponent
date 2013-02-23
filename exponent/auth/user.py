"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore


class User(item.Item):
    uid = attributes.bytes(allowNone=False)

    @classmethod
    def withUid(cls, rootStore, uid):
        return cls._getStore(rootStore, uid).findUnique(cls)


    @classmethod
    def _getStore(cls, rootStore, uid):
        return substore.getStore(rootStore, ["users", uid])


    @classmethod
    def createStore(cls, rootStore, uid):
        return substore.createStore(rootStore, ["users", uid])
