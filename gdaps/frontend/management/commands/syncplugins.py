import logging

from gdaps.frontend import current_engine
from gdaps.pluginmanager import PluginManager
from gdaps.management.commands.syncplugins import Command as SyncPluginsCommand

logger = logging.getLogger(__name__)


class Command(SyncPluginsCommand):
    """This command adds frontend capabilities to GDAPS' base syncplugins command.."""

    help = "Synchronizes all plugins into the database, and includes frontends."

    def handle(self, *args, **options) -> None:
        """Synchronizes all found plugins into the database."""

        super().handle(*args, **options)
        current_engine().update_plugins_list(
            [app.path for app in PluginManager.plugins()]
        )
