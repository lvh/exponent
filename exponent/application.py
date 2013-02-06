"""
Tools for running exponent applications.
"""
from axiom import store
from twisted import plugin
from twisted.application import service
from twisted.python import usage
from zope import interface


class Options(usage.Options):
    """
    The options for starting a service.
    """
    optParameters = [
        ["store", "s", None, "Path to root store (mandatory)", store.Store]
    ]

    def postParameters(self):
        if self["store"] is None:
            raise usage.UsageError("Passing a root store is mandatory.")



@interface.implementer(plugin.IPlugin, service.IServiceMaker)
class ServiceMaker(object):
    """
    Makes an exponent service from the command line.
    """
    tapname = "exponent"
    description = "An exponent service."
    options = Options

    def makeService(self, options):
        return service.IService(options["store"])
