import os

from django.apps import AppConfig, apps
from django.conf import settings
from gdaps.apps import GdapsConfig

import gdaps
from gdaps import PluginError
from gdaps.conf import gdaps_settings
from gdaps.apps import GdapsConfig


class FrontendPluginMeta:
    version = gdaps.__version__
    visible = False
    author = GdapsConfig.PluginMeta.author
    email = GdapsConfig.PluginMeta.author_email
    category = GdapsConfig.PluginMeta.category


class FrontendConfig(AppConfig):
    name = "gdaps.frontend"
    label = "frontend"
    verbose_name = "GDAPS frontend"

    PluginMeta = FrontendPluginMeta

    def ready(self):

        if "webpack_loader" not in [app.name for app in apps.get_app_configs()]:
            raise PluginError(
                "The 'gdaps.frontend' module relies on django-webpack-loader. "
                "Please add 'webpack_loader' to your INSTALLED_APPS."
            )
