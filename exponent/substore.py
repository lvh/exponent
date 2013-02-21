from axiom import substore


def createStore(rootStore, pathSegments):
    """
    Creates a substore under the given root store with the given path.
    """
    return substore.SubStore.createNew(rootStore, pathSegments).open()


def getStore(rootStore, pathSegments):
    """
    Gets a substore under the given root store with the given path.
    """
    storePath = rootStore.filesdir
    for segment in pathSegments:
        storePath = storePath.child(segment)
    withThisPath = substore.SubStore.storepath == storePath
    return rootStore.findUnique(substore.SubStore, withThisPath).open()
