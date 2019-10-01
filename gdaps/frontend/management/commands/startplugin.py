import logging
import os
import sys

from django.apps import apps

from gdaps.frontend import current_engine
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.startplugin import Command as GdapsStartPluginCommand

logger = logging.getLogger(__name__)


class Command(GdapsStartPluginCommand):
    """Overrides gdaps' startplugin command and adds frontend features to it."""

    help = (
        "Creates a basic GDAPS plugin structure in the "
        f"'{GdapsStartPluginCommand.plugin_path}/' directory from a template"
        ", including a frontend package."
    )

    def handle(self, name, **options):

        self.templates.append(
            os.path.join(
                apps.get_app_config("frontend").path,
                "management",
                "templates",
                "plugin",
            )
        )
        super().handle(name, **options)

        # get all plugins, including
        all_plugin_names = [
            app.name.replace(PluginManager.group + ".", "")
            for app in PluginManager.plugins()
        ] + [name]
        if options["verbosity"] >= 2:
            logger.info("Found plugins:\n")
            for plugin in all_plugin_names:
                logger.info("  " + plugin + "\n")

        current_engine().update_plugins_list(all_plugin_names)
