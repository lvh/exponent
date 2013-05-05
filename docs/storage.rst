===================================
 Long-term storage and write locks
===================================

Eventually, stores are written to permanent storage. There are a few
reasons for this:

* Persistence: while individual application servers can and will fail to
  provide persistence, permanent storage can be highly redundant and
  resilient with fairly high tolerance for reduced bandwidth or latency
* Cost: slow, durable storage is typically available at lower prices
  than highly performant local storage
* Load balancing: while individual application servers have limited
  capacity, shared permanent storage allows other application servers to
  take over the load.

Write lock directories and write locks
======================================

.. py:module:: exponent.directory

At any given point in time, exactly zero or one hosts hold the write
lock. This is guaranteed by forcing them to acquire the write lock
from a write lock directory. The two relevant interfaces are
``IWriteLockDirectory`` and ``IWriteLock``.

.. autointerface:: IWriteLockDirectory

.. autointerface:: IWriteLock

Dealing with partial failure
----------------------------

An example of a partial failure case would be one where there are two
application servers, one holding the lock to a particular store,
followed by a network partition that renders the former unable to
communicate.

.. ditaa::

                        +---------------------+
                        | Lock directory      |
                        | cGRE                |
                        +-+-----------------+-+
                          |                 |
                          |                 |
       +------------------+-+             +-+------------------+
       | Application server |             | Application server |
       | #1 cYEL            |             | #2 cYEL            |
       +--+-----------------+             +--------------------+
          |
       +--+----+
       | Lock  |
       | cRED  |
       +-------+

Then, the network partition occurs:

.. ditaa::

                        +---------------------+
     Lock forfeited     | Lock directory      |
                        | cGRE                |
                        +-+-----------------+-+
    ----------------------+----\            |
                          |    |            |
       +------------------+-+  |          +-+------------------+
       | Application server |  :          | Application server |
       | #1 cYEL            |  |          | #2 cYEL            |
       +--+-----------------+  |          +--+-----------------+
          |                    |             |     
       +--+----+               |          +--+----+
       | Lock  |               |          | Lock  | Re-issued lock
       | cRED  |   Separated   |          | cRED  | after forfeit
       +-------+   partition   |          +-------+


In this figure, the lock is forfeited, and then re-issued to a new
application server.

.. ditaa::

                        +---------------------+
                        | Lock directory      |
                        | cGRE                |
                        +-+-----------------+-+
                          |                 |
                          |                 |
       +------------------+-+             +-+------------------+
       | Application server |             | Application server |
       | #1 cYEL            |             | #2 cYEL            |
       +--+-----------------+             +--+-----------------+
          |                                  |                               
       +--+----+                          +--+----+
       | Lock  |                          | Lock  |
       | cRED  |                          | cRED  |
       +-------+                          +-------+


Finally, the network partition is restored. Both application servers
are convinced they still hold the lock.

Please note that although drawn here as a single, separate entity, the
lock directory itself may well be implemented as a distributed system.

The interface of ``IWriteLock`` prevents this. While the disconnected
host may still mistakenly believe that it holds the write lock, writes
made using it will fail. Unfortunately, this means that the data that
was on the application server holding the lock is lost, assuming the
stores can not be reconciled later.

A suitable tradeoff between partition tolerance, availability and
consistency has to be picked. Automatic reconcilability is often only
a very incomplete answer. If a user sees that some actions were not
completed, he or she may choose to complete a *very similar yet subtly
different* action. If reconciled, both actions would be shown, and
manual intervention is still needed to properly reconcile.

The eventual solution to this problem will probably consist of a
combination of proactive, regular store persisting, and possibly
read-only access for users whose store is currently being recovered
from a failing node.

Handling scheduled events
-------------------------

Scheduled events can only be run when there is an active reactor (and
therefore application server) to run them.

Future features
===============

The following features are currently not yet supported.

In-use writing
--------------

Currently, it's only possible to throw data away

This effectively makes the user's interactions with the service
transactional. That sounds a lot better than it is. For example, a
user holding open a connection effectively prevents their data from
being stored anywhere else.

There are a few approaches to fixing this.

Optimistic copying
~~~~~~~~~~~~~~~~~~

SQLite is generally pretty durable, so we may be able to pull off
reading a store in-use after all. More research here is required.

Unfortunately, this can result in inconsistencies. For example, if the
user adds a picture, which consists both of an Axiom item and an
actual file, it's possible that:

* The file is copied, but the item isn't (image disappears)
* The other way around (image is referenced but doesn't exist)

Snapshots
---------

It may be useful to have snapshot backups of stores.

Differential updates
--------------------

Typically only small portions of the store are updated. Especially for
large stores, it would make sense to only update differentials instead
of the entire store.

This could be done by sending ``bsdiff``/``xdiff`` diffs of the
tarball as acquired when acquiring the write lock.
