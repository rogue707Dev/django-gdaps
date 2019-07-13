import string
import logging

from django.core.exceptions import ObjectDoesNotExist, ImproperlyConfigured
from django.core.management import call_command
from django.core.management.base import BaseCommand, no_translations
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.migrations.executor import MigrationExecutor
from django.utils.translation import gettext_lazy as _

from gdaps import PluginError
from gdaps.exceptions import IncompatibleVersionsError
from gdaps.models import GdapsPlugin
from gdaps.pluginmanager import PluginManager
from semantic_version import Version

logger = logging.getLogger(__name__)


def _snake_case_to_spaces(name):
    return string.capwords(name, "_").replace("_", " ")


class Command(BaseCommand):
    """This is the management command to initialize a plugin the first time.

    It calls the 'initialize' method of all plugins"""

    help = "Calls the 'initialize' method of all plugins."

    # TODO: add support for initializing ONE plugin
    # missing_args_message = "You must provide a plugin name."

    # def add_arguments(self, parser):
    #     parser.add_argument("plugin_name", help=self.help, type=str)

    # __db_synchronized = None
    #
    # def is_database_synchronized(self, database):
    #     # cached flag if db is in sync, taken from migrate cmd
    #     if self.__db_synchronized is None:
    #         connection = connections[database]
    #         connection.prepare_database()
    #         executor = MigrationExecutor(connection)
    #         targets = executor.loader.graph.leaf_nodes()
    #         self.__db_synchronized = False if executor.migration_plan(targets) else True
    #
    #     return self.__db_synchronized

    def handle(self, *args, **options):
        """calls all plugins' `initialize` methods"""

        for app in PluginManager.plugins():
            # first, try to fetch this plugin from the DB - if doesn't exist, create and initialize it.
            # if it exists, check if there is an update available.
            try:
                plugin = GdapsPlugin.objects.get(name=app.name)
                file_version = app.PluginMeta.version
                if Version(file_version) > Version(plugin.version):
                    pass
                    # there is a newer version available on disk

                    # FIXME: check PluginMeta.compatibility

                    # if self.is_database_synchronized():
                    #     # at this point, the db is in sync with the files according to Django.
                    #     # we can now check if there is code waiting to execute.
                    #     pass
                    #
                    # raise PluginError(
                    #     "Plugin version upgrade detected. Please the 'migrate' management command to update plugins."
                    # )

            except ObjectDoesNotExist:
                # if it doesn't exist, it is a new plugin.
                # Let's initialize it.
                plugin = GdapsPlugin()
                plugin.name = app.name

                meta = app.PluginMeta

                plugin.verbose_name = getattr(
                    meta, "verbose_name", app.name.replace("_", " ").capitalize()
                )
                plugin.author = getattr(meta, "author", _("unknown"))
                plugin.author_email = getattr(meta, "author_email", "")
                plugin.category = getattr(meta, "category", _("Miscellaneous"))
                plugin.description = getattr(meta, "description", "")
                plugin.visible = getattr(meta, "visible", True)

                try:
                    version = getattr(meta, "version", "1.0.0")
                    v = Version(version)
                    plugin.version = version
                except ValueError as e:
                    raise ImproperlyConfigured(
                        "Plugin '{}'version number is incorrect: '{}'".format(
                            app.name, version
                        )
                    )

                # TODO: add compatibility check
                plugin.compatibility = getattr(meta, "compatibility", "")

                plugin.save()

                if hasattr(app, "initialize"):
                    try:
                        app.initialize()
                    except Exception as E:
                        raise PluginError(
                            "Error calling initialize method of '{}' plugin".format(
                                app.name
                            )
                        )
