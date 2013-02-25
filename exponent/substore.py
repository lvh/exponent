from axiom import substore
from functools import partial


def createStore(rootStore, pathSegments):
    """
    Creates amd returns substore under the given root store with the given
    path segments.
    """
    return substore.SubStore.createNew(rootStore, pathSegments).open()


def getStore(rootStore, pathSegments):
    """
    Gets a substore under the given root store with the given path segments.

    Raises ``axiom.errors.ItemNotFound`` if no such store exists.
    """
    storePath = rootStore.filesdir
    for segment in pathSegments:
        storePath = storePath.child(segment)
    withThisPath = substore.SubStore.storepath == storePath
    return rootStore.findUnique(substore.SubStore, withThisPath).open()


def withSubstores(cls):
    """
    A class decorator for classes to have ``createStore`` and ``getStore``,
    prefixed with their type name, and adds a convenience function
    ``findUnique`` that finds a unique instance of ``cls`` in a substore,
    given by root store and path segments.

    Returns the class itself (with the new methods).
    """
    cls.createStore = partial(_prefixedWithTypeName, cls, createStore)
    cls.getStore = partial(_prefixedWithTypeName, cls, getStore)
    cls.findUnique = partial(_findUnique, cls)
    return cls


def _prefixedWithTypeName(cls, f, rootStore, *pathSegments):
    """
    Calls ``f`` with the given ``rootStore`` and the given ``pathSegments``,
    prefixed with the class' type name.
    """
    return f(rootStore, (cls.typeName,) + pathSegments)


def _findUnique(cls, rootStore, *pathSegments):
    """
    Finds a unique instance of ``cls`` in a substore of ``rootStore`` with the
    given path segments.

    This assumes the class has the ``getStore`` class method provided by the
    decorator, and is not intended for external use.
    """
    return cls.getStore(rootStore, *pathSegments).findUnique(cls)
