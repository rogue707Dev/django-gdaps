import logging

from gdaps.frontend import current_engine
from gdaps.management.commands.syncplugins import Command as BaseSyncPluginsCommand

logger = logging.getLogger(__name__)


class Command(BaseSyncPluginsCommand):
    """This command adds frontend capabilities to GDAPS' base syncplugins command.."""

    help = "Synchronizes all plugins into the database, and installs their frontend packages."

    def handle(self, *args, **options) -> None:
        """Synchronizes all found plugins into the database."""

        super().handle(*args, **options)
        current_engine().update_plugins_list()
