======================
 User name resolution
======================

.. py:module:: exponent.auth.name

Internally, exponent uses user identifiers to refer to users. These
are random strings of sufficient length that they are guaranteed to be
unique.

Authentication mechanisms should always use this identifier. On the
other hand, users clearly won't remember a random string with 320 bits
worth of entropy. Therefore, there is a generic mechanism for turning
user names into uids.

User names are not supposed to change regularly, so clients are
encouraged to cache these aggressively.

Implementing a name resolution method
=====================================

The interface for name resolvers is ``INameResolver``.

.. autointerface:: INameResolver
