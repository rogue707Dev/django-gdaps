Installation
------------

Install GDAPS in your Python virtual environment (pipenv is preferred):

.. code-block:: bash

    pipenv install gdaps
    # or: pip install gdaps


Create a Django application as usual: ``manage.py startproject myproject``.

Now add "gdaps" to the ``INSTALLED_APPS`` section, and add a special line below it:

.. code-block:: python

    from gdaps.pluginmanager import PluginManager

    INSTALLED_APPS = [
        # ... standard Django apps and GDAPS
        "gdaps",
        # if you also want frontend support, add:
        # "gdaps.frontend"
        # "webpack_loader",
    ]
    # The following line is important: It loads all plugins from setuptools
    # entry points and from the directory named 'myproject.plugins':
    INSTALLED_APPS += PluginManager.find_plugins("myproject.plugins")

You can use whatever you want for your plugin path, but we recommend that you use "**<myproject>.plugins**" here to make things easier. See :doc:`usage`.

For further frontend specific instructions, see :ref:`frontend-support`.

Basically, this is all you really need so far, for a minimal working
GDAPS-enabled Django application.


.. _Usage: usage
