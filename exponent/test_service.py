from axiom import attributes, item, store
from exponent import service
from twisted.application import service as tas
from twisted.protocols import amp
from twisted.trial import unittest


class ServiceTests(unittest.TestCase):
    def test_implementsInterface(self):
        self.assertTrue(tas.IService.implementedBy(service.Service))


    def test_startService(self):
        """
        Checks that the service adapts its store to ``IBoxReceiver``, wraps it
        with a factory, and gets that factory to start listening on the
        service's stored endpoint.
        """
        testStore = store.Store()

        boxReceiver = object()
        testStore.inMemoryPowerUp(boxReceiver, amp.IBoxReceiver)
        endpoint = FakeEndpoint(store=testStore)

        testService = service.Service(store=testStore, endpoint=endpoint)
        testService.startService()

        self.assertEqual(endpoint.factory._boxReceiver, boxReceiver)



class FakeEndpoint(item.Item):
    """
    A pretend server endpoint.
    """
    _dummy = attributes.boolean()
    factory = attributes.inmemory()

    def listen(self, factory):
        """
        Remembers the factory that was being listened with.
        """
        self.factory = factory


class FactoryTests(unittest.TestCase):
    def test_buildProtocol(self):
        """
        Tests that the factory builds protocols that use the factory's box
        receiver.
        """
        boxReceiver = object()
        factory = service.Factory(boxReceiver)
        protocol = factory.buildProtocol(object())
        self.assertIdentical(protocol.boxReceiver, boxReceiver)
