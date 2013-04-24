========================
 Session authentication
========================

Registering a username without a password
=========================================

The client calls 

Requesting a session identifier
===============================

The client logs in using some alternative method. The client then
calls ``RequestSession``. It returns the user identifier and the
session identifier. The client stores these.

Logging in using a session
==========================

The client logs in by calling ``LoginSession`` with the user's
identifier and a valid session identifier. It returns a new session
identifier. The client stores the new session identifier.

This invalidates the old session identifier.
