Installation
------------

Create a Django application as usual: ``manage.py startproject myproject``.

Now install ``gdaps`` as usual app:

.. code-block:: python

    from gdaps.pluginmanager import PluginManager

    INSTALLED_APPS = [
        # ... standard Django apps and GDAPS
        "gdaps",
        # if you also want frontend support, add:
        #"gdaps.frontend"
        # "myproject.plugins.fooplugin",
        # "webpack_loader",
    ]
    # The following line is important: It loads all plugins from setuptools
    # entry points and from the directory named 'myproject.plugins':
    INSTALLED_APPS += PluginManager.find_plugins("myproject.plugins")


We recommend that you use myproject.**plugins**.
For further frontend specific instructions, see `Frontend
support <#frontend-support>`_.

The configuration of GDAPS is bundled in one namespace ``GDAPS``:

.. code-block:: python

   GDAPS = { "FRONTEND_DIR": "frontend", }

Also see `Settings <#settings]>`__.

Basically, this is all you really need so far, for a minimal working
GDAPS-enabled Django application.