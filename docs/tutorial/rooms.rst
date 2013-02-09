==============
 Adding rooms
==============

Next, we will add rooms to our text-based adventure.

Rooms should have neighboring rooms in one or more directions: north, east,
south and west. We could store this in multiple ways:

 - four extra attributes on each room (``to(North|East|South|West)``)
 - objects representing the connection between rooms

In this tutorial, we pick the latter, because it separates the
concerns of the room itself versus the connections between them.

Since there are several possible implementations for a connection between
rooms, we'll implement an interface for it, documenting what exactly it means
to be a connection between rooms.



Let's write the tests for this:

.. literalinclude:: escape/test/test_rooms.py

Here's an example implementation that makes those tests pass:

.. literalinclude:: escape/rooms.py
