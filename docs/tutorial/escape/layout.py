"""
Tools for creating random room layouts.
"""
from escape import rooms
from random import choice


def createLayout(store):
    allRooms = [_createRandomRoom(store) for _ in xrange(10)]

    mainCorridors = [allRooms[0:3], allRooms[3:7], allRooms[7:10]]
    for corridor in mainCorridors:
        _makeCorridor(corridor, "N")

    crossCorridor = [choice(corridor) for corridor in mainCorridors]
    _makeCorridor(crossCorridor, "E")


ROOM_SHAPES = [
    "square",
    "rectangular",
    "circular",
    "weirdly-shaped"
]

MATERIALS = [
    "stone",
    "sandstone",
    "highly polished granite",
    "jell-o",
    "glass",
    "wood"
]

WALL_DECORATIONS = [
    "nothing",
    "bugs",
    "mold",
    "someone's last words, written in blood,"
    "a bunch of brightly-lit torches",
    "a plethora of expensive-looking rugs",
    "a collection of eerie paintings"
]

DESCRIPTION_TEMPLATE = (
    "You are in a {shape} room with {wall_material} walls and "
    "{floor_material} floors. There's {decoration} on the walls."
)


def _createRandomRoom(store, _choice=choice):
    description = DESCRIPTION_TEMPLATE.format(
        shape=_choice(ROOM_SHAPES),
        wall_material=_choice(MATERIALS),
        floor_material=_choice(MATERIALS),
        decoration=_choice(WALL_DECORATIONS)
    )
    return rooms.Room(store=store, description=description)


def _makeCorridor(rooms, direction):
    for start, end in zip(rooms, rooms[1:]):
        rooms.Hallway(
            store=start.store,  # end.store is the same thing
            fromRoom=start,
            toRoom=end,
            direction=direction
        )
