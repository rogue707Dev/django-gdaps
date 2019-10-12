from django.apps import AppConfig, apps

import gdaps
from gdaps import PluginError
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
