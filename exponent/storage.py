"""
Long-term storage for Axiom stores.
"""
import weakref

from axiom import attributes, item, store
from exponent import exceptions
from twisted.internet import defer
from zope import interface


class IStorage(interface.Interface):
    """
    Read-only access to ong-term storage for stores.
    """
    def get(self, pathSegments):
        """
        Gets a store from long-term storage.
        """



@interface.implementer(IStorage)
class FakeStorage(item.Item):
    _dummy = attributes.boolean()
    _cache = attributes.inmemory()

    def activate(self):
        self._cache = weakref.WeakValueDictionary()


    def get(self, pathSegments):
        storePath = self.store.filesdir.descendant(pathSegments)
        try:
            return defer.succeed(self._cache[storePath])
        except KeyError:
            pass

        if not storePath.exists():
            return defer.fail(exceptions.NoSuchStoreException())

        requestedStore = self._cache[storePath] = store.Store(storePath)
        return defer.succeed(requestedStore)
