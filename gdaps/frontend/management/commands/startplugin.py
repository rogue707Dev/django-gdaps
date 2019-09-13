import os
import string
import logging
import sys

import django

from django.conf import settings
from django.apps import apps

from gdaps import PluginError
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.startplugin import Command as StartPluginCommand

logger = logging.getLogger(__name__)


class Command(StartPluginCommand):
    """This overrides gdaps' startplugin command and adds frontend features to it."""

    help = (
        "Creates a basic GDAPS plugin structure in the "
        "'{}/' directory from a template, including a frontend package.".format(
            StartPluginCommand.plugin_path
        )
    )

    def handle(self, name, **options):
        super().handle(name, **options)

        frontend_path = os.path.join(settings.BASE_DIR, "frontend")
        if not os.path.exists(frontend_path):
            try:
                os.makedirs(frontend_path)
            except:
                raise PluginError(
                    f"Could not create frontend directory '{frontend_path}'."
                )

        # get all plugins, including
        all_plugins = [app.name for app in PluginManager.plugins()]
        # FIXME: DEBUG
        sys.stdout.write("plugins: ")
        for plugin in all_plugins:
            sys.stdout.write(plugin)

        # write plugins into js file, to be collected dynamically by webpack
        try:
            plugins_file = open(os.path.join(frontend_path, "plugins.js"), "w")
            plugins_file.write("module.exports = [\n")
            for app in all_plugins:
                plugins_file.write(os.path.join(self.plugin_path, app.name, "frontend"))
            plugins_file.write("]\n")
        except:
            raise PluginError(
                "Could not open plugins.js for writing. Please check write permissions in {}.".format(
                    frontend_path
                )
            )
        finally:
            plugins_file.close()
