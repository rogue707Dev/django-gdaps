from django.apps import AppConfig
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from gdaps import require_app


class GrapheneConfig(AppConfig):
    name = "gdaps.graphene"

    def ready(self):
        require_app(self, "graphene_django")
