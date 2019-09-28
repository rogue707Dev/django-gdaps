import string
import logging
import sys

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.management.base import BaseCommand, no_translations
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.utils.translation import gettext_lazy as _

import gdaps
from gdaps.api import IGdapsPlugin
from gdaps.apps import PluginConfig
from gdaps.exceptions import PluginError
from gdaps.models import GdapsPlugin
from gdaps.pluginmanager import PluginManager
from semantic_version import Version

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """This is the management command to sync all installed plugins into the database."""

    help = "Synchronizes all plugins into the database."
    verbosity = 0

    __db_synchronized = False

    def log(self, verbosity, message):
        if self.verbosity >= verbosity:
            sys.stdout.write(message)

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            nargs="?",
            type=str,
            help="synchronizes only plugins from specific database",
        )

    def is_database_synchronized(self, database=None):
        # cached flag if db is in sync, taken from migrate mgmt cmd
        if not database:
            database = "default"
        if not self.__db_synchronized:
            connection = connections[database]
            connection.prepare_database()
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            self.__db_synchronized = False if executor.migration_plan(targets) else True

        return self.__db_synchronized

    @staticmethod
    def _copy_plugin_to_db(app: PluginConfig, db_plugin: GdapsPlugin) -> None:
        meta = app.pluginMeta
        db_plugin.name = app.name
        db_plugin.verbose_name = getattr(
            meta, "verbose_name", app.name.replace("_", " ").capitalize()
        )
        db_plugin.author = getattr(meta, "author", _("unknown"))
        db_plugin.author_email = getattr(meta, "author_email", "")
        db_plugin.vendor = getattr(meta, "vendor", "")
        db_plugin.category = getattr(meta, "category", _("Miscellaneous"))
        db_plugin.description = getattr(meta, "description", "")
        db_plugin.visible = getattr(meta, "visible", True)
        db_plugin.version = app.pluginMeta.version
        db_plugin.compatibility = getattr(meta, "compatibility", "")

        db_plugin.save()

    def handle(self, *args, **options) -> None:
        """Synchronizes all found plugins into the database.

        Only plugins that are activated vie INSTALLED_APPS or installed via pip/pipenv and found by the
        PluginManager are taken into account.
        """
        self.verbosity = options["verbosity"]
        if not options["database"]:
            options["database"] = "default"

        self.log(3, "Searching for plugins...\n")
        for app in PluginManager.plugins():
            # first, try to fetch this plugin from the DB - if doesn't exist, create and initialize it.
            # if it exists, check if there is an update available.
            self.log(3, f"  * {app.name}\n")
            try:
                # noinspection PyUnresolvedReferences
                db_plugin = GdapsPlugin.objects.get(name=app.name)

                file_version = app.pluginMeta.version
                if Version(file_version) > Version(db_plugin.version):
                    # there is a newer version available on disk

                    # TODO: check pluginMeta.compatibility here

                    self.log(
                        0,
                        f"There is a newer version of the '{app.verbose_name}' plugin available.\n",
                    )

                    for database in settings.DATABASES.keys():
                        if not self.is_database_synchronized(database):
                            raise PluginError(
                                "Plugin version upgrade detected. Please run the 'migrate' management "
                                "command first to update plugins."
                            )

                    # at this point, the db is in sync with the files according to Django.
                    # we can now update all db fields with that from the plugin on disk
                    # this is necessary as the author e.g. could change during plugin development
                    self._copy_plugin_to_db(app, db_plugin)

                    # we can now check if there is code waiting to execute.
                    # TODO: run upgrade procedure of plugin

            except ObjectDoesNotExist:
                # if it doesn't exist, it is a new plugin.
                # Let's initialize it.
                self.log(3, f"Found new plugin '{app.verbose_name}'.\n")
                db_plugin = GdapsPlugin()
                version = None
                try:
                    version = app.pluginMeta.version
                    v = Version(version)
                    db_plugin.version = version
                except ValueError:
                    raise ImproperlyConfigured(
                        f"Plugin '{app.name}' version number is incorrect: '{version}'"
                    )
                self._copy_plugin_to_db(app, db_plugin)

                # TODO: add compatibility check

                if hasattr(app.pluginMeta, "initialize"):
                    try:
                        app.pluginMeta.initialize()
                    except Exception as E:
                        raise PluginError(
                            f"Error calling initialize method of '{app.name}' plugin"
                        )

            # plugin hook after plugins are synchronized to DB
            for ep in gdaps.ExtensionPoint(IGdapsPlugin):
                ep.plugin_synchronized(app)

        # are there plugins in the database that do not exist on disk?
        self.log(2, "Searching for orphaned plugins...\n")

        for plugin in PluginManager.orphaned_plugins():  # type: GdapsPlugin
            self.log(2, f"  * {plugin.name}: ")
            if self.is_database_synchronized(options["database"] or None):
                plugin.delete()
                self.log(2, "removed from database.\n")
            else:
                self.log(2, "\n")
        else:
            self.log(3, "  None found.\n")
