import logging
import os
import shutil
import subprocess

from django.apps import apps
from django.core.management import CommandError

from gdaps.frontend import current_engine
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.startplugin import Command as GdapsStartPluginCommand
from gdaps.conf import gdaps_settings

logger = logging.getLogger(__name__)


class Command(GdapsStartPluginCommand):
    """Overrides gdaps' startplugin command and adds frontend features to it."""

    help = (
        "Creates a basic GDAPS plugin structure in the "
        f"'{GdapsStartPluginCommand.plugin_path}/' directory from a template"
        ", including a frontend package."
    )

    def handle(self, name, **options):

        if shutil.which("npm") is None:
            raise CommandError("npm is not available, please install it.")

        self.templates.append(
            os.path.join(
                apps.get_app_config("frontend").path,
                "management",
                "templates",
                "plugin",
            )
        )
        self.extensions += current_engine().extensions
        self.extra_files += current_engine().extra_files

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

        subprocess.check_call(
            "npm init",
            cwd=os.path.join(GdapsStartPluginCommand.plugin_path, name, gdaps_settings.FRONTEND_DIR),
            shell=True,
        )

        current_engine().update_plugins_list(all_plugin_names)
