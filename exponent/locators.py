"""
Locator base classes.
"""
from twisted.protocols import amp


class Locator(amp.CommandLocator):
    """
    A command locator that takes a store.

    This is intended to be persisted by ``maxims.named.remember``.
    """
    def __init__(self, store):
        self.store = store
