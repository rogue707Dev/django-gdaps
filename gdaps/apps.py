import sys

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured


# copied / adapted from Pretix
class PluginConfig(AppConfig):
    """Base config class for GDAPS plugins.

    All GDAPS plugin apps files need to have an AppConfig class which inherits from ``PluginConfig``.
    It is a convenience class that checks for the existence of the PluginMeta inner class, and provides
    some basic methods that are needed when interacting with a plugin during its life cycle.

    .. code-block:: python

        from django.utils.translation import gettext_lazy as _
        from gdaps.apps import PluginConfig

        class FooPluginConfig(PluginConfig):

            class PluginMeta:
                # the plugin machine "name" is taken from the Appconfig, so no name here
                verbose_name = _('Foo Plugin')
                author = 'Me Personally'
                description = _('A foo plugin')
                visible = True
                version = '1.0.0'
                compatibility = "myproject.core>=2.3.0"

    If you are using signals in your plugin, we recommend to put them into a ``signals`` submodule.
    Import them from the ``AppConfig.ready()`` method.

    .. code-block:: python

            def ready(self):
                # Import signals if necessary:
                from . import signals  # NOQA


    .. seealso::
        Don't overuse the ``ready`` method. Have a look at the `Django documentation of ready()
        <https://docs.djangoproject.com/en/2.2/ref/applications/#django.apps.AppConfig.ready>`_.

    If your plugin needs to install some data into the database at the first run, you can provide a ``initialize``
    method, which will be called using the ``initializeplugins`` management command:

    .. code-block:: bash

        ./manage.py initializeplugins

    Do all necessary things there that need to be done when the plugin is available the first time, e.g. after
    installing a plugin using pip/pipenv.

    .. code-block:: python

        def initialize(self):
            # install some fixtures, etc.
            pass

    """

    name = "gdaps"

    # shamelessly copied from Pretix
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.name == "gdaps":
            # ignore GDAPS itself
            return

        if not hasattr(self, "PluginMeta"):
            raise ImproperlyConfigured(
                "A GDAPS plugin config must have a PluginMeta inner class."
            )

        if hasattr(self.PluginMeta, "compatibility"):
            import pkg_resources

            try:
                pkg_resources.require(self.PluginMeta.compatibility)
            except pkg_resources.VersionConflict as e:
                print("Incompatible plugins found!")
                print(
                    "Plugin {} requires you to have {}, but you installed {}.".format(
                        self.name, e.req, e.dist
                    )
                )

                sys.exit(1)
