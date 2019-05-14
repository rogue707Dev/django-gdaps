import os

from django.apps import AppConfig, apps
from django.conf import settings

from gdaps import PluginError


class FrontendConfig(AppConfig):
    name = "gdaps.frontend"
    label = "frontend"
    verbose_name = "GDAPS frontend"

    def ready(self):

        if "webpack_loader" not in [app.name for app in apps.get_app_configs()]:
            raise PluginError(
                "The 'gdaps.frontend' module relies on django-webpack-loader. Please add 'webpack_loader' to your INSTALLED_APPS."
            )

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
