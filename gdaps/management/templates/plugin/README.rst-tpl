{{ camel_case_app_name }} Plugin
================================

This is a newly created plugin for {{ project_title }}.
Please add some documentation here. 

General
-------

{{ project_title }} modules are living in the ``{{ plugin_path }}`` setuptools entrypoint group.
They are normal Django apps, but found and loaded dynamically during startup.
As Django apps, they can have everything a "static" app also has:

PluginConfig = AppConfig
^^^^^^^^^^^^^^^^^^^^^^^^

The app configuration which should be declared in the module's ``apps.py``.

Migrations
^^^^^^^^^^

The *migrations* directory is scanned during startup, and missing
migrations should be done using ``./manage.py migrate``

Models
^^^^^^

Create your models as usual in ``models.py``, they will be included. Don't forget to run ``makemigrations`` and ``migrate`` afterwords.
