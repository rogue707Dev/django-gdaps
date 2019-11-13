Installation
============

Install GDAPS in your Python virtual environment (pipenv is preferred):

.. code-block::bash

    pipenv install gdaps
    # or: pip install gdaps


Create a Django application as usual: ``manage.py startproject myproject``.

Now add "gdaps" to the ``INSTALLED_APPS`` section, and add a special line below it:

.. code-block:: python

    from gdaps.pluginmanager import PluginManager

    INSTALLED_APPS = [
        # ... standard Django apps and GDAPS
        # if you also want frontend support, add:
        "gdaps",
    ]
    # The following line is important: It loads all plugins from setuptools
    # entry points and from the directory named 'myproject.plugins':
    INSTALLED_APPS += PluginManager.find_plugins("myproject.plugins")

You can use whatever you want for your plugin path, but we recommend that you use "**<myproject>.plugins**" here to make things easier. See :doc:`usage`.

Basically, this is all you really need so far, for a minimal working
GDAPS-enabled Django application.

Frontend support
----------------

If you want to add frontend support too your project, you need to do as follows:

Add ``gdaps.frontend`` (before  ``gdaps``), and ``webpack_loader`` to Django.

.. code-block::bash

    pipenv install django-webpack-loader


.. code-block:: python

    # settings.py

    from gdaps.pluginmanager import PluginManager

    INSTALLED_APPS = [
        # ... standard Django apps and GDAPS
        "gdaps.frontend"
        "gdaps",
        "webpack_loader",  # you'll need that too
    ]
    INSTALLED_APPS += PluginManager.find_plugins("myproject.plugins")

Now, to satisfy webpack-loader, add a section to settings.py:

.. code-block:: python

    WEBPACK_LOADER = {
        'DEFAULT': {
            'STATS_FILE': os.path.join(BASE_DIR, "frontend", 'webpack-stats.json'),
        }
    }

This is because django(-webpack-loader) needs to find the info file webpack creates at
each compile, so that files can be recognized by django's reloading mechanism.

Another section is needed for GDAPS:

.. code-block:: python

    GDAPS = {
        "FRONTEND_ENGINE": "vue",
    }

There are some keys here to configure:

FRONTEND_DIR
    This is the directory for the frontend, relative to DJANGO_ROOT.
    Default is "frontend".

FRONTEND_ENGINE
    The engine which is used for setting up a frontend. ATM it can only be "vue". In future, maybe other engines are supported (Angular, React, etc.). PRs welcome.

FRONTEND_PKG_MANAGER
    This is the package manager used to init/install packages. ATM you can use "yarn" or "npm". Default is *npm*.

and finally add the URL path for redirecting all to the frontend engine:

.. code-block:: python

    # urls.py
    from gdaps.pluginmanager import PluginManager

    urlpatterns = PluginManager.urlpatterns() + [
        # ... add your fixed URL patterns here, like "admin/", etc.
    ]

Now you can initialize the frontend with

.. code-block:: bash

    ./manage.py initfrontend

This creates a basic boilerplate (previously created with 'vue create' and calls *yarn install* to
install the needed javascript packages.

