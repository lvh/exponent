==================================================
 Getting the character to interact with the rooms
==================================================

While our game hsa rooms now, they're pretty boring: they don't actually do
anything, and there's no way for the player to interact with them.

We're going to create a command.

Most commands live in a responder locator. A responder locator is simply
something that finds responders (implementations of a given command) for the
other side of the connection.

Looking around
==============

First and foremost, a character should be able to look around and describe his
surroundings to the player. This should contain a description of the current
room and anything in it, and places to go next.

Moving between rooms
====================

Secondly, a player should be able to move between rooms.

This command introduces a new feature: errors and error reporting.
