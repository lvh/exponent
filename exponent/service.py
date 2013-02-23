from axiom import attributes, item
from twisted.application import service
from twisted.internet import protocol
from twisted.protocols import amp
from zope import interface


@interface.implementer(service.IService)
class Service(item.Item):
    """
    A service that adapts its store to a box receiver and then serves that
    from a stored endpoint.
    """
    endpoint = attributes.reference()

    def startService(self):
        """
        Adapts the store to a box receiver, instantiates the stored endpoint.
        """
        factory = Factory(amp.IBoxReceiver(self.store))
        return self.endpoint.listen(factory)



class Factory(protocol.Factory):
    """
    A factory that produces binary AMP box protocols for a given box receiver.
    """
    def __init__(self, boxReceiver):
        self._boxReceiver = boxReceiver


    def buildProtocol(self, addr):
        return amp.BinaryBoxProtocol(self._boxReceiver)
