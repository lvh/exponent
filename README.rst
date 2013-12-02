==========
 exponent
==========

``exponent`` is an experimental toolkit for building applications with
a fractal architecture.

Uses a number of other technologies:

- Twisted_, an event-driven networking engine
- Axiom_, an object serialization layer for SQLite
- AMP_, an RPC protocol
- Foolscap_, an object-capability library for distributed systems

.. _Twisted: https://www.twistedmatrix.com
.. _Axiom: https://pypi.python.org/pypi/axiom
.. _AMP: http://amp-protocol.net
.. _Foolscap: http://foolscap.lothar.com/trac

Changelog
=========

0.0.3 (and before) (WIP)
------------------------

There were several tiny releases grabbing things from an internal
project, so they've been coalesced here.

Features:

- Locators
- Filesystem-based long-term storage
- In-memory write lock (directory) for long-term storage
- Basic authentication framework; token-based, so multi-factor auth ready
- Rudimentary tutorial
