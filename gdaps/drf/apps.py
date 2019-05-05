from django.apps import AppConfig
from django.apps import apps

from gdaps import PluginError


class DrfConfig(AppConfig):
    name = "gdaps.drf"

    def ready(self):

        if "rest_framework" not in [app.name for app in apps.get_app_configs()]:
            raise PluginError(
                "The 'gdaps.drf' module relies on Django REST Framework. Please add 'rest_framework' to your INSTALLED_APPS."
            )
