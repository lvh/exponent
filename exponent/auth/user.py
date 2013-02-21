"""
The base model for users.
"""
from axiom import attributes, item
from exponent import substore


class User(item.Item):
    uid = attributes.bytes(allowNone=False)

    @classmethod
    def withUid(cls, rootStore, uid):
        userStore = substore.getStore(rootStore, ["users", uid])
        return userStore.findUnique(cls)
