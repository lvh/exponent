from axiom import errors
from escape import rooms
from twisted.trial import unittest


class RoomTests(unittest.TestCase):
    def test_create(self):
        rooms.Room(description="A room")



class HallwayTest(unittest.TestCase):
    def setUp(self):
        self.rooms = [
            rooms.Room(description="A white room"),
            rooms.Room(description="A red room")
        ]


    def test_connect(self):
        hallway = rooms.Hallway(
            fromRoom=self.rooms[0],
            toRoom=self.rooms[1],
            direction="N",
        )

        for room in self.rooms:
            self.assertIn(hallway, room.getConnections())

        self._assertConnections(self.rooms[0], {"N": hallway})
        self._assertConnections(self.rooms[0], {"S": hallway})


    def _assertConnected(self, room, connections):
        for direction in "NESW":
            try:
                connection = connections[direction]
                self.assertEqual(room.getConnection(direction), connection)
            except KeyError:
                getConnection = lambda: room.getConnection(direction)
                self.assertRaises(errors.ItemNotFound, getConnection)
