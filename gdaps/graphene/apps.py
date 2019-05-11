from django.apps import AppConfig
from django.apps import apps

from gdaps import PluginError


class GrapheneConfig(AppConfig):
    name = "gdaps.graphene"

    def ready(self):

        if "graphene_django" not in [app.name for app in apps.get_app_configs()]:
            raise PluginError(
                "The 'gdaps.graphene' module relies on Graphene. Please add 'graphene_django' to your INSTALLED_APPS."
            )
