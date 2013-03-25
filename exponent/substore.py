"""
Helpers for substores and items that are first-class children of root stores.
"""
from axiom import substore


def createChildStore(rootStore, pathSegments):
    """
    Creates amd returns substore under the given root store with the given
    path segments.
    """
    return substore.SubStore.createNew(rootStore, pathSegments).open()


def getChildStore(rootStore, pathSegments):
    """
    Gets a child store under the root store with these path segments.

    Raises ``axiom.errors.ItemNotFound`` if no such store exists.
    """
    storePath = rootStore.filesdir
    for segment in pathSegments:
        storePath = storePath.child(segment)
    withThisPath = substore.SubStore.storepath == storePath
    return rootStore.findUnique(substore.SubStore, withThisPath).open()


class ChildMixin(object):
    """
    A mixin for Item classes that are first-class children of a root store.
    """
    @classmethod
    def createChildStore(cls, rootStore, pathSegments):
        """
        Creates a child store under the root store with these path segments.
        """
        pathSegments = [cls.typeName] + list(pathSegments)
        return createChildStore(rootStore, pathSegments)


    @classmethod
    def getChildStore(cls, rootStore, pathSegments):
        """
        Gets a child store under the root store with these path segments.
        """
        pathSegments = [cls.typeName] + list(pathSegments)
        return getChildStore(rootStore, pathSegments)


    @classmethod
    def findUniqueChild(cls, rootStore, pathSegments):
        """
        Finds a unique instance of ``cls`` in a child store of ``rootStore``
        with the given path segments.
        """
        childStore = cls.getChildStore(rootStore, pathSegments)
        return childStore.findUnique(cls)
