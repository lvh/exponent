=================================================
 Upgrading your application with existing stores
=================================================

Upgrading Axiom items
=====================

Whenever a new store is attached, the Axiom upgrader service will
automatically search it for items that have new schemas versions
available, running them in sequence until the item is fully upgraded.
Thus, in order to keep items upgraded, just write plain old Axiom
upgraders.

Upgrading code
==============

Since command locators are the only interface your application
provides, and they are stored in the Axiom store by their fully
qualified dotted name, just updating the code is sufficient.

Adding new features
===================

Existing stores will not automatically get access to any locator you
specify (otherwise, users would get access to administrative features,
for example).

This is a conscious feature. It allows you to integrate new features
in your code continuously, selectively enabling or disabling them for
some users. People have implemented similar behavior in existing
projects (these are often called "feature flags"). Exponent allows you
to cleanly separate the behavior itself from those who have access to
it.

Enabling and disabling feature availability for new users.
----------------------------------------------------------

TBD
