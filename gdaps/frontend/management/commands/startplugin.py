import os
import string
import logging
import sys

import django

from django.conf import settings

from gdaps import PluginError
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.startplugin import Command as StartPluginCommand

logger = logging.getLogger(__name__)


class Command(StartPluginCommand):
    """This overrides gdaps' startplugin command and adds frontend features to it."""

    help = (
        "Creates a basic GDAPS plugin structure in the "
        f"'{StartPluginCommand.plugin_path}/' directory from a template, including a frontend package."
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
        all_plugin_names = [
            app.name.replace(PluginManager.group + ".", "")
            for app in PluginManager.plugins()
        ] + [name]
        if options["verbosity"] >= 2:
            sys.stdout.write("Found plugins:\n")
            for plugin in all_plugin_names:
                sys.stdout.write("  " + plugin + "\n")

        # write plugins into js file, to be collected dynamically by webpack
        try:
            plugins_file = open(os.path.join(frontend_path, "plugins.js"), "w")
            plugins_file.write("module.exports = [\n")
            counter = 1
            total = len(all_plugin_names)
            for app_name in all_plugin_names:
                plugins_file.write(
                    '  "'
                    + os.path.join(
                        self.plugin_path,
                        app_name.replace(PluginManager.plugin_path(), ""),
                        "frontend",
                    )
                    + '"'
                )
                if counter < total:
                    plugins_file.write(",")
                plugins_file.write("\n")
                counter += 1

            plugins_file.write("]\n")
        except Exception as e:
            raise PluginError(
                str(e)
                + "\n "
                + f"Could not open plugins.js for writing. Please check write permissions in {frontend_path}."
            )
        finally:
            plugins_file.close()
