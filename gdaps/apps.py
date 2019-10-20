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

        .. note::
            If ``PluginMeta`` is missing, the plugin is not recognized by GDAPS.
        """

    #: The version of the plugin, following `Semantic Versioning <https://semver.org/>`_. This is
    #: used for dependency checking as well, see ``compatibility``.
    version = "0.0.0"

    verbose_name = "My special plugin"

    #: The author of the plugin. Not translatable.
    author = "Me, myself and Irene"

    #: The email address of the author
    author_email = "me@example.com"

    #: A longer text to describe the plugin.
    description = ""

    #: A freetext category where your plugin belongs to.
    #: This can be used in your application to group plugins.
    category = "GDAPS"

    #: A boolean value whether the plugin should be visible, or hidden.
    #:
    #:     .. deprecated:: 0.4.2
    #:         Use `hidden` instead.
    visible = True

    #:A boolean value whether the plugin should be hidden, or visible. False by default.
    hidden = False

    #: A string containing one or more other plugins that this plugin is known being compatible with, e.g.
    #: "myproject.core>=1.0.0<2.0.0" - meaning: This plugin is compatible with ``myplugin.core`` from version
    #: 1.0.0 to 1.x - v2.0 and above is incompatible.
    #:
    #:         .. note:: Work In Progress.

    compatibility = "gdaps>=1.0.0"

    def initialize(self):
        """
        Callback to initialize the plugin.

        If your plugin needs to install some data into the database at the first run, you can provide this
        method to ``PluginMeta``. It will be called when ``manage.py syncplugins`` is called and the plugin
        is run the first time.

        An example would be installing some fixtures, providing a message to the user etc.
        """


class GdapsPluginMeta:
    version = gdaps.__version__
    verbose_name = "Generic Django Application Plugin System"
    author = "Christian Gonzalez"
    author_email = "christian.gonzalez@nerdocs.at"
    category = "GDAPS"
    visible = False


class GdapsConfig(AppConfig):
    name = "gdaps"
    PluginMeta = GdapsPluginMeta

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
