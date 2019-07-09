
GDAPS - Generic Django Apps Plugin System
=========================================

Welcome to the GDAPS documentation!

This site contains information about how to use GDAPS and add "pluggability" to your Django projects.

A standard Django "app" is *reusable* (if done correctly), but is not *pluggable*,
like being distributed and "plugged" into a Django main application without modifications.

If you want to create a Django application that makes use of "plugins" that can extend your project later,
this library is right for you. It consists of a few bells and twistles where Django lacks "automagic":

* Apps are automatically found using pkgtools' entry points
* Apps can provide their own URLs (they are included and merged into urlpatterns automatically)
* Apps can define ``Interfaces``, that other GDAPS apps then can implement
* Apps can provide Javascript frontends that are found and compiled automatically (WorkInProgress)

The reason you want to use GDAPS, is: **you want to create an application that should be extended via plugins**:

.. warning::
    This software is in a very early development state.
    It could eat your dog, or create wormholes below your bed.
    Use it at your own risk.
    **You have been warned.**



.. toctree::
    :maxdepth: 2
    :caption: Table of Contents

    Introduction
    Installation
    usage
    APIs
    Contributing


License
=======

I'd like to give back what I received from many Open Source software packages, and keep this
library as open as possible, and it should stay this way.
GDAPS is licensed under the `General Public License, version 3 <https://www.gnu.org/licenses/gpl-3.0-standalone.html>`_.


Indices and tables
==================

* :ref:`genindex`
