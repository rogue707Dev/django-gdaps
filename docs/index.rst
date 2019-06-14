
GDAPS - Generic Django Apps Plugin System
=========================================


This library allows Django to make real "pluggable" apps.

A standard Django "ap p" is *reusable* (if done correctly), but is not *pluggable*,
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

   usage/installation
   usage/usage



Contributing
============

If you want to contribute, feel free and write a PR, or contact me.


License
=======

I'd like to give back what I received from many Open Source software packages, and keep this
library as open as possible, and it should stay so.
GDAPS is licensed under the `GPL <https://www.gnu.org/licenses/gpl.html>`_, see LICENSE


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
