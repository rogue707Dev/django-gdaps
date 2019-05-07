import os
import logging
import subprocess
import threading

from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import (
    Command as RunserverCommand,
)

from gdaps.conf import gdaps_settings

logger = logging.getLogger(__name__)


class Npm(threading.Thread):
    def run(self):
        subprocess.run(
            "npm run serve --prefix {}".format(
                os.path.join(settings.BASE_DIR, gdaps_settings.FRONTEND_DIR)
            ),
            shell=True,
            check=True,
        )


class Command(RunserverCommand):
    """Overrides 'runserver' and starts a'npm run serve' thread in the background.

    This creates some problems as Django's server is also restarted when a file changed,
    thus restarting the whole npm compile process with every file change.

    So this command is deactivated ATM.
    """

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

    def inner_run(self, *args, **options):

        self.stdout.write("Starting 'npm run serve'...\n")

        npm = Npm()
        npm.start()

        super().inner_run(*args, **options)

        npm.join()
