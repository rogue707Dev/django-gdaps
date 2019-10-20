import logging
import sys

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

import gdaps
from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__file__)


class PluginMeta:
    """Inner class of GDAPS plugins.

    All GDAPS plugin AppConfig classes need to have an inner class named ``PluginMeta``. This
    PluginMeta provides some basic attributes and  methods that are needed when interacting with a
    plugin during its life cycle.

    .. note::
        If ``PluginMeta`` is missing, the plugin is not recognized. You don't have to inherit this class
        here, just name it "PluginMeta".

    .. code-block:: python

        from django.utils.translation import gettext_lazy as _
        from django.apps import AppConfig

        class FooPluginConfig(AppConfig):

            class PluginMeta:
                # the plugin machine "name" is taken from the Appconfig, so no name here
                verbose_name = _('Foo Plugin')
                author = 'Me Personally'
                description = _('A foo plugin')
                visible = True
                version = '1.0.0'
                compatibility = "myproject.core>=2.3.0"




    .. seealso::
        Don't overuse the ``ready`` method. Have a look at the `Django documentation of ready()
        <https://docs.djangoproject.com/en/2.2/ref/applications/#django.apps.AppConfig.ready>`_.

    If your plugin needs to install some data into the database at the first run, you can provide a ``initialize``
    method to ``PluginMeta``, which will be called using the ``initializeplugins`` management command:

    .. code-block::bash

        ./manage.py initializeplugins

    Do all necessary things there that need to be done when the plugin is available the first time, e.g. after
    installing a plugin using pip/pipenv.

    .. code-block:: python

        class PluginMeta:
            def initialize(self):
                # install some fixtures, etc.
                pass

    Signals
        If you are using signals in your plugin, we recommend to put them into a ``signals`` submodule.
        Import them from the ``AppConfig.ready()`` method.

        .. code-block:: python

                def ready(self):
                    # Import signals if necessary:
                    from . import signals  # NOQA
    """

    version = gdaps.__version__
    verbose_name = "Generic Django Application Plugin System"
    author = "Christian Gonzalez"
    author_email = "christian.gonzalez@nerdocs.at"
    category = "GDAPS"
    visible = False


class GdapsConfig(AppConfig):
    name = "gdaps"
    PluginMeta = PluginMeta

    def ready(self):
        # walk through all installed plugins and check some things
        for app in PluginManager.plugins():
            if hasattr(app.PluginMeta, "compatibility"):
                import pkg_resources

                try:
                    pkg_resources.require(app.PluginMeta.compatibility)
                except pkg_resources.VersionConflict as e:
                    logger.critical("Incompatible plugins found!")
                    logger.critical(
                        f"Plugin {app.name} requires you to have {e.req}, but you installed {e.dist}."
                    )

                    sys.exit(1)
