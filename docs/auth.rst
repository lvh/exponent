========================
 Authentication methods
========================

User name resolution
====================

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
-------------------------------------

The interface for name resolvers is ``INameResolver``.

.. autointerface:: INameResolver

Session authentication
======================

Registering a user name without a password
-----------------------------------------

The client calls 

Requesting a session identifier
-------------------------------

The client logs in using some alternative method. The client then
calls ``RequestSession``. It returns the user identifier and the
session identifier. The client stores these.

Logging in using a session
--------------------------

The client logs in by calling ``LoginSession`` with the user's
identifier and a valid session identifier. It returns a new session
identifier. The client stores the new session identifier.

This invalidates the old session identifier.
