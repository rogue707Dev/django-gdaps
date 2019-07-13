import os
import string
import logging
import django

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError, BaseCommand, no_translations
from django.apps import apps

from gdaps import PluginError
from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__name__)


def _snake_case_to_spaces(name):
    return string.capwords(name, "_").replace("_", " ")


class Command(BaseCommand):
    """This is the management command to initialize a plugin the first time.

    It calls the 'initialize' method of all plugins"""

    help = "Calls the 'initialize' method of all plugins."

    # FIXME: implement initializing single plugins
    # missing_args_message = "You must provide a plugin name."

    @no_translations
    def handle(self, *args, **options):
        try:
            for app in PluginManager.plugins():
                # call all plugins' `initialize` methods

                # FIXME: initialize() is not required to be idempotent
                # It should be made sure that either plugins are responsible for this method being idempotent,
                # or calling it just once. For the second, it's necessary to save the "initialized" state somewhere.
                # Using a DB flag is not a good option, as it requires some projects to use a DB model
                # without needing it.
                if hasattr(app, "initialize"):
                    logger.error(app.name)
                    app.initialize()

        except Exception as E:
            raise PluginError(
                "Error calling initialize method of '{}' plugin".format(app.name)
            )
