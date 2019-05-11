import os

from django.apps import AppConfig
from django.conf import settings


class FrontendConfig(AppConfig):
    name = "gdaps.frontend"
    label = "frontend"
    verbose_name = "GDAPS frontend"

    def ready(self):

        settings.WEBPACK_LOADER.update(
            {
                "GDAPS": {
                    "STATS_FILE": os.path.join(
                        # FIXME: use dynamic frontend dir
                        settings.BASE_DIR,
                        "frontend",
                        "webpack-stats.json",
                    )
                }
            }
        )
