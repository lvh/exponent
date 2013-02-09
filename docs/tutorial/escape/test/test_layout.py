from escape import layout, rooms
from twisted.trial import unittest


class CreateRandomRoomTests(unittest.TestCase):
    def test_createRoom(self):
        shape, material, decoration = "square", "stone", "nothing"

        def choice(choices):
            if choices is layout.ROOM_SHAPES:
                return shape
            elif choices is layout.MATERIALS:
                return material
            elif choices is layout.WALL_DECORATIONS:
                return decoration

        room = layout._createRandomRoom(None, choice)
        expectedDescription = layout.DESCRIPTION_TEMPLATE.format(
            shape=shape,
            wall_material=material,
            floor_material=material,
            decoration=decoration
        )
        self.assertEqual(room.description, expectedDescription)


class MakeCorridorTests(unittest.TestCase):
    def test_makeCorridorGoingNorth(self):
        corridor = []
        for idx in xrange(10):
            room = rooms.Room(description="Room {}".format(idx))
            corridor.append(room)

        layout._makeCorridor(corridor, direction="N")
