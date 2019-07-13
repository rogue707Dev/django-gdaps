Usage
=====


Creating plugins
----------------

Create plugins using a Django management command:

.. code-block:: bash

    ./manage.py startplugin fooplugin

This command asks a few questions, creates a basic Django app in the plugin path chosen in ``PluginManager.find_plugins()``. It provides useful defaults as well as a setup.py/setup.cfg file.

If you use git in your project, install the ``gitpython`` module (``pip/pipenv install gitpython --dev``). ``startplugin`` will determine your git user/email automatically and use at the right places.

You now have two choices for this plugin:

* add it statically to ``INSTALLED_APPS``: see `Static plugins <#static-plugins>`__.
* make use of the dynamic loading feature: see `Dynamic plugins <#dynamic-plugins>`__.

Static plugins
^^^^^^^^^^^^^^

In most of the cases, you will ship your application with a few
"standard" plugins that are statically installed. These plugins must be
loaded *after* the ``gdaps`` app.

.. code:: python

    # ...

    INSTALLED_APPS = [
        # ... standard Django apps and GDAPS
        "gdaps",

        # put "static" plugins here too:
        "myproject.plugins.fooplugin.apps.FooConfig",
    ]

This plugin app is loaded as usual, but your GDAPS enhanced Django application
can make use of it's GDAPS features.

Dynamic plugins
^^^^^^^^^^^^^^^

By installing a plugin with pip/pipenv, you can make your application
aware of that plugin too:

.. code:: bash

    pipenv install -e myproject/plugins/fooplugin

This installs the plugin as python module into the site-packages and
makes it discoverable using setuptools. From this moment on it should be
already registered and loaded after a Django server restart. Of course
this also works when plugins are installed from PyPi, they don't have to
be in the project's ``plugins`` folder. You can conveniently start
developing plugins in there, and later move them to the PyPi repository.

.. _Interfaces:


The plugin AppConfig
--------------------

Django recommends to point ot the app's AppConfig directly in INSTALLED_APPS. You should do that too with GDAPS plugins. Plugins that are installed via pip(env) are found automatically, as their AppConfig class must be named after the Plugin.

Plugins' AppConfigs must inherit from ``gdaps.apps.PluginConfig``, and provide an inner class ``PluginMeta``. For more information see :class:`gdaps.apps.PluginConfig`.


Interfaces
----------

Plugins can define interfaces, which can then be implemented by other
plugins. The ``startplugin`` command will create a ``<app_name>/api/interfaces.py`` file automatically.
It's not obligatory to put all Interface definitions in that module, but it is a recommended coding style for GDAPS plugins:

.. code:: python

    from gdaps import Interface

    class IFooInterface(Interface):
        """Documentation of the interface"""

        class Meta:
            service = True

        def do_something(self):
            pass

Interfaces can have a default Meta class that defines Interface options.
Available options:

service
    If ``service=True`` (which is the default), then all implementations are
    instantiated instantly at definition time, having a full class instance
    availably at any time. Iterations over ExtensionPoints return the instances directly.

    If you use ``service=False``, the plugin is not instantiated, and
    iterations over ExtensionPoints will return **classes**, not instances.
    This sometimes may be the desired functionality, e.g. for data classes, or classes that
    just return staticmethods.

ExtensionPoints
---------------

An ExtensionPoint (EP) is a plugin hook that refers to an Interface. An
EP can be defined anywhere in code. You can then get all the plugins
that implement that interface by just iterating over that
ExtensionPoint:

\`\`\`python from gdaps import ExtensionPoint from
myproject.plugins.fooplugin.api.interfaces import IFooInterface

class MyPlugin: ep = ExtensionPoint(IFooInterface)

::

    def foo_method(self):
        for plugin in ep:
            print plugin().do_domething()

\`\`\`

Keep in mind that iterating over an ExtensionPoint **does not return
instances** of plugins. It just returns the **class** that was decorated
with *@implements*. This might be improved in the future
(auto-instantiated plugins).

.. _Implementations:

Implementations
---------------

You can then easily implement this interface in any other file (in this
plugin or in another plugin) using the ``@implements`` decorator syntax:

.. code:: python

    from gdaps import implements
    from myproject.plugins.fooplugin.api.interfaces import IFooInterface

    @implements(IFooInterface)
    class OtherPluginClass:

        def do_something(self):
            print('I did something!')

I didn't want to force implementations to inherit a ``Plugin`` base
class, like some other plugin systems do. This would mean that
implementations won't be as flexible as I wanted them. When just using a
decorator, you can easily use ANY, even your already existing, class and
just ducktype-implement the methods the Interface demands. If you forget
to implement a method, GDAPS will complain instantly.


Extending Django's URL patterns
-------------------------------

To let your plugin define some URLs that are automatically detected by your Django application, you
have to add some code to your global urls.py file:

.. code:: python

    from gdaps.pluginmanager import PluginManager

    urlpatterns =  [
        # add your fixed, non-plugin paths here.
    ]

    # just add this line after the urlpatterns definition:
    urlpatterns += PluginManager.urlpatterns()

GDAPS then loads and imports all available plugins' *urls.py*  files,
collects their ``urlpatterns`` variables and merges them into the global
one.

A typical ``fooplugin/urls.py`` would look like this:

.. code:: python

    from . import views

    app_name = fooplugin

    urlpatterns =  [
        path("/fooplugin/myurl", views.MyUrlView.as_view()),
    ]

GDAPS lets your plugin create global, root URLs, they are not
namespaced. This is because soms plugins need to create URLS for
frameworks like DRF, etc. Plugins are responsible for their URLs, and
that they don't collide with others.

.. _Settings:

Per-plugin Settings
-------------------

GDAPS allows your application to have own settings for each plugin
easily, which provide defaults, and can be overridden in the global
``settings.py`` file. Look at the example conf.py file (created by
``./manage.py startplugin fooplugin``), and adapt to your needs:

.. code:: python

    from django.test.signals import setting_changed
    from gdaps.conf import PluginSettings

    NAMESPACE = "FOOPLUGIN"

    # Optional defaults. Leave empty if not needed.
    DEFAULTS = {
        "MY_SETTING": "somevalue",
        "FOO_PATH": "django.blah.foo",
        "BAR": [
            "baz",
            "buh",
        ],
    }

    # Optional list of settings that are allowed to be in "string import" notation. Leave empty if not needed.
    IMPORT_STRINGS = (
        "FOO_PATH"
    )

    # Optional list of settings that have been removed. Leave empty if not needed.
    REMOVED_SETTINGS = ( "FOO_SETTING" )


    fooplugin_settings = PluginSettings("FOOPLUGIN", None, DEFAULTS, IMPORT_STRINGS)

Detailed explanation:

DEFAULTS
   The ``DEFAULTS`` are, as the name says, a default array of settings. If
   ``fooplugin_setting.BLAH`` is not set by the user in settings.py, this
   default value is used.

IMPORT_STRINGS
   Settings in a *dotted* notation are evaluated, they return not the
   string, but the object they point to. If it does not exist, an
   ``ImportError`` is raised.

REMOVED_SETTINGS
   A list of settings that are forbidden to use. If accessed, an
   ``RuntimeError`` is raised.

   This allows very flexible settings - as dependant plugins can easily
   import the ``fooplugin_settings`` from your ``conf.py``.

   However, the created conf.py file is not needed, so if you don't use
   custom settings at all, just delete the file.


.. _frontend-support:

Frontend support
----------------

GDAPS supports Javascript frontends for building e.g. SPA applications.
ATM only Vue.js ist supported, but PRs are welcome to add more (Angular,
React?).

If you add ``gdaps.frontend`` to ``INSTALLED_APPS``, there is a new
management command available: ``manage.py initfrontend``. It has one
mandatory parameter, the frontend engine:

:: code-block:: bash

    ./manage.py initfrontend vue

This creates a /frontend/ directory in the project root. Change into
that directory and run ``yarn install`` once to install all the
dependencies of Vue.js needed.

It is recommended to install vue globally, you can do that with
``yarn global add @vue/cli @vue/cli-service-global``.

Now you can start ``yarn serve`` in the frontend directory. This starts
a development web server that bundles the frontend app using webpack
automatically. You then need to start Django using
``./manage.py runserver`` to enable the Django backend. GDAPS manages
all the needed background tasks to transparently enable hot-reloading
when you change anything in the frontend source code now.
