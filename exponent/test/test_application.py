import mock

from exponent import application
from twisted import plugin
from twisted.application import service
from twisted.python import usage
from twisted.trial import unittest


class OptionsTests(unittest.TestCase):
    def setUp(self):
        self.options = application.Options()


    def test_withRootStore(self):
        self.options["store"] = "xyzzy"
        self.options.postParameters()


    def test_noRootStore(self):
        self.assertRaises(usage.UsageError, self.options.postParameters)



class ServiceMakerTests(unittest.TestCase):
    def test_interfaces(self):
        """
        Tests that the ``ServiceMaker`` class is both an ``IPlugin`` and an
        ``IServiceMaker``.
        """
        for i in [service.IServiceMaker, plugin.IPlugin]:
            i.implementedBy(application.ServiceMaker)


    def test_usesOptions(self):
        """
        Asserts that the service maker uses the appropriate options.
        """
        options = application.ServiceMaker.options
        self.assertIdentical(options, application.Options)


    def test_makeService(self):
        """
        Tests that ``makeService`` adapts the passed store to an ``IService``
        and then starts it.
        """
        store = object()
        serviceMaker = application.ServiceMaker()

        with mock.patch("twisted.application.service.IService") as s:
            service = serviceMaker.makeService({"store": store})
            s.assert_called_once_with(store)
            self.assertEqual(s.return_value, service)
