import os
import string
import logging
import sys

from gdaps.frontend import current_engine
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

        # get all plugins, including
        all_plugin_names = [
            app.name.replace(PluginManager.group + ".", "")
            for app in PluginManager.plugins()
        ] + [name]
        if options["verbosity"] >= 2:
            sys.stdout.write("Found plugins:\n")
            for plugin in all_plugin_names:
                sys.stdout.write("  " + plugin + "\n")

        current_engine().update_plugins_list(all_plugin_names)
