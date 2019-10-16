import logging
import os
import shutil
import importlib

from django.apps import apps
from django.core.management import CommandError

from gdaps.frontend import current_engine, frontend_settings
from gdaps.frontend.pkgmgr import current_package_manager
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.startplugin import Command as GdapsStartPluginCommand

logger = logging.getLogger(__name__)

from nltk.stem import PorterStemmer


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

        stemmer = PorterStemmer()
        # use singular name for plugin frontend packages,
        #  e.g. "myproject-plugins" -> "myproject-plugin-foobar" - mind the missing s
        plugin_frontend_name = (
            f"{stemmer.stem(PluginManager.group.replace('.', '-'))}-{name}"
        )

        self.templates.append(
            os.path.join(
                apps.get_app_config("frontend").path,
                "management",
                "templates",
                "plugin",
            )
        )
        self.rewrite_template_suffixes += current_engine().rewrite_template_suffixes
        self.extra_files += current_engine().extra_files
        self.context.update({"plugin_frontend_name": plugin_frontend_name})

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

        module = importlib.import_module(f"{PluginManager.group}.{name}")
        current_package_manager().init(
            os.path.join(
                GdapsStartPluginCommand.plugin_path,
                name,
                frontend_settings.FRONTEND_DIR,
                plugin_frontend_name,
            ),
            version=module.__version__,
        )
