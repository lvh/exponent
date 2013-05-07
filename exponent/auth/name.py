"""
Tools for mapping names to user identifiers.
"""
from axiom import attributes, errors as ae, item
from exponent._util import synchronous
from exponent.auth import errors as eae, user
from zope import interface


class INameResolver(interface.Interface):
    """
    Resolves users' names to user identifiers.
    """
    def resolve(name):
        """
        Resolve a name.

        :param name: The name to resolve.
        :type name: ``unicode``
        
        :return: A ``Deferred`` that will fire with the user identifier or
            ``BadCredentials`` if the name could not be resolved.
        """



@interface.implementer(INameResolver)
class _NameReferenceResolver(item.Item):
    """
    A name resolve that uses local items.
    """
    _dummy = attributes.boolean()

    @synchronous
    def resolve(self, name):
        _UUR = _UserIdentifierNameReference

        try:
            self.store.findUnique(_UUR, _UUR.name == name)
        except ae.ItemNotFound:
            raise eae.BadCredentials()

        reference = self.store.findUnique(_UUR, _UUR.name == name)
        return user.User.findUniqueChild(self.store, reference.identifier)



class _UserIdentifierNameReference(item.Item):
    """
    A reference to match a user identifier to a name.
    """
    identifier = attributes.bytes(allowNone=False, indexed=True)
    name = attributes.text(allowNone=False, indexed=True)










