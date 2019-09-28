import string
import logging

from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand, no_translations
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.migrations.executor import MigrationExecutor
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

from gdaps.apps import PluginConfig
from gdaps.exceptions import IncompatibleVersionsError, PluginError
from gdaps.models import GdapsPlugin
from gdaps.pluginmanager import PluginManager
from semantic_version import Version

logger = logging.getLogger(__name__)


def _snake_case_to_spaces(name):
    return string.capwords(name, "_").replace("_", " ")


class Command(BaseCommand):
    """This is the management command to sync all installed plugins into the database."""

    help = "Synchronizes all plugins into the database."

    __db_synchronized = None

    def is_database_synchronized(self, database):
        pass
        # # cached flag if db is in sync, taken from migrate cmd
        # if self.__db_synchronized is None:
        #     connection = connections[database]
        #     connection.prepare_database()
        #     executor = MigrationExecutor(connection)
        #     targets = executor.loader.graph.leaf_nodes()
        #     self.__db_synchronized = False if executor.migration_plan(targets) else True
        #
        # return self.__db_synchronized

    @staticmethod
    def _copy_plugin_to_db(app: PluginConfig, db_plugin: Model) -> None:
        # noinspection PyUnresolvedReferences
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
        """synchronizes all plugins into the database."""

        for app in PluginManager.plugins():
            # first, try to fetch this plugin from the DB - if doesn't exist, create and initialize it.
            # if it exists, check if there is an update available.
            try:
                # noinspection PyUnresolvedReferences
                db_plugin = GdapsPlugin.objects.get(name=app.name)

                file_version = app.pluginMeta.version
                if Version(file_version) > Version(db_plugin.version):
                    # there is a newer version available on disk

                    # TODO: check pluginMeta.compatibility here

                    self.stdout.write(
                        f"There is a newer version of the '{app.verbose_name}' plugin available.\n"
                    )

                    if not self.is_database_synchronized():
                        raise PluginError(
                            "Plugin version upgrade detected. Please run the 'migrate' management command to update plugins."
                        )

                    # at this point, the db is in sync with the files according to Django.
                    # we can now update all db fields with that from the plugin on disk
                    # this is necessary as the author e.g. could change during plugin development
                    self._copy_plugin_to_db(app, db_plugin)

                    # we can now check if there is code waiting to execute.

            except ObjectDoesNotExist:
                # if it doesn't exist, it is a new plugin.
                # Let's initialize it.
                self.stdout.write(f"Found new plugin '{app.verbose_name}'.\n")
                db_plugin = GdapsPlugin()
                version = None
                try:
                    version = getattr(app.pluginMeta, "version", "1.0.0")
                    v = Version(version)
                    db_plugin.version = version
                except ValueError as e:
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
