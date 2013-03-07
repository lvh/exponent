==========
 Tutorial
==========

In this tutorial, we'll build a simple persisted to-do app.

Models
======

The to-do app has at least one obvious model: the to-do item. We'll be
producing to-do items with a mandatory and unique description (because
we'll use it to reference the to-do item), a boolean flag showing
whether or not the item has been completed, and an optional due date.
Additionally, the model should have a convenience property to check if
it is overdue.

Let's write some tests to check this functionality:

.. literalinclude:: todo/test/test_models.py

Here's a simple implementation that passes the tests:

.. literalinclude:: todo/models.py

Commands
========

There's a few obvious commands our to-do app should have:

 - Add a to-do item, optionally with a due date
 - List to-do items, optionally listing completed ones
 - Complete a to-do item

Again, we'll write the tests for these commands first. We write these
tests by attempting to serialize some known-good data, and check that
doesn't raise an exception.

Here's a test case that does just this:

.. literalinclude:: todo/test/test/commands.py
    :pyobject: CommandTestCase

Adding a to-do item
-------------------

.. literalinclude:: todo/test/test_commands.py
    :pyobject: AddTodoItemTests

.. literalinclude:: todo/commands.py
    :pyobject: AddTodoItem

Note that we are using ``txampext``'s ``typeFor`` function, which
automatically returns the appropriate AMP type for a given Axiom
attribute. That way, if the Axiom type changes, the AMP command will
immediately be of the appropriate type. We'll use the same function in
future definitions.

Listing to-do items
-------------------

.. literalinclude:: todo/test/test_commands.py
    :pyobject: ListTodoItemsTests

.. literalinclude:: todo/commands.py
    :pyobject: ListTodoItems


Completing to-do items
----------------------

.. literalinclude:: todo/test/test_commands.py
    :pyobject: CompleteTodoItemTests

.. literalinclude:: todo/commands.py
    :pyobject: CompleteTodoItem


Implementations
===============

Finally, we'll write some implementations for these commands.

Adding a to-do item
-------------------

Client
======

