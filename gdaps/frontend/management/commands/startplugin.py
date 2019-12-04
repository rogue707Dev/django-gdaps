import logging
import os
import shutil

from django.apps import apps
from django.core.management import CommandError

from gdaps.frontend import current_engine, frontend_settings
from gdaps.frontend.pkgmgr import current_package_manager
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
        if shutil.which(current_package_manager().name) is None:
            raise CommandError(
                f"{current_package_manager().name} is not available, please install it."
            )

        self.templates.append(
            os.path.join(
                apps.get_app_config("gdaps_frontend").path,
                "engines",
                current_engine().name,
                "templates",
                "plugin",
            )
        )
        self.rewrite_template_suffixes += current_engine().rewrite_template_suffixes
        self.extra_files += current_engine().extra_files

        super().handle(name, **options)

        # get all plugins, including new one
        all_plugin_names = [
            app.name.replace(PluginManager.group + ".", "")
            for app in PluginManager.plugins()
        ] + [name]
        if options["verbosity"] >= 2:
            logger.info("Found plugins:\n")
            for plugin in all_plugin_names:
                logger.info("  " + plugin + "\n")
