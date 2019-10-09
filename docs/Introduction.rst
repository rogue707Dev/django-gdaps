Introduction
============

This library allows Django to make real "pluggable" apps.

A standard Django "app" is *reusable* (if done correctly), but is not *pluggable*,
like being distributed and "plugged" into a Django main application without modifications. GDAPS is filling this gap.

The reason you want to use GDAPS is: **you want to create an application that should be extended via plugins**. GDAPS consists of a few bells and twistles where Django lacks "automagic":

GDAPS apps...
* are automatically found using setuptools' entry points
* can provide their own URLs which are included and merged into urlpatterns automatically
* can define ``Interfaces``, that other GDAPS apps then can implement
* can provide Javascript frontends that are found and compiled automatically (WorkInProgress)


GDAPS working modes
-------------------

The "observer pattern" plugin system is completely decoupled from the PluginManager
(which manages GDAPS pluggable Django apps), so basically you have two choices to use GDAPS:

Simple
    Use :ref:`Interfaces`, and :ref:`Implementations`  **without a plugin/module system**. It's not necessary to divide your application into GDAPS apps to use GDAPS.
    Just code your application as usual and have an
    easy-to-use "observer pattern" plugin system.

    * Define an interface
    * Create one or more implementations for it and
    * iterate over the interface to get all plugins.

    Just *importing* the python files with your implementations will make them work.

    Use this if you just want to structure your Django software using an "observer pattern".
    This is used  within  GDAPS itself, for the Javascript frontend implementations
    (e.g. Vue.js).

Full
    Use GDAPS as **complete module/app system**.

    * You'll have to add "gdaps" to your INSTALLED_APPS first.
    * Create plugins using the ``startplugin`` managemant command, and install them via pip/pipenv.

    You have a :ref:`PluginManager` available then, and after a ``manage.py migrate``
    and ``manage.py syncplugins``,
    Django will have all GDAPS plugins recognized as models too, so you can easily
    administer them in your Django admin.

    This mode enables you to create fully-fledged extensible applications with real
    plugins that can be written by different parties and distributed via PyPi.

    See :ref:`usage` for further instructions.
