from axiom import attributes, item, queryutil as q
from zope import interface


class IRoomConnection(inteface.Interface):
    """
    A connection between two rooms.
    """
    direction = interface.Attribute("""
        The direction in which the room connection points.
    """)


class Room(item.Item):
    description = attributes.text(allowNone=False)


    def _connected(self):
        return q.OR(Hallway.fromRoom == self, Hallway.toRoom == self)


    def getConnections(self):
        return self.store.query(Hallway, self._connected())


    def getConnection(self, direction):
        connected = q.AND(self._connected(), Hallway.direction == direction)
        return self.store.findUnique(Hallway, connected)



class Hallway(item.Item):
    """
    A two-way hallway.
    """
    fromRoom = attributes.reference(allowNone=False)
    toRoom = attributes.reference(allowNone=False)
    direction = attributes.text(allowNone=False)

    def traverse(self, reverse=False):
        return toRoom if not reverse else fromRoom
