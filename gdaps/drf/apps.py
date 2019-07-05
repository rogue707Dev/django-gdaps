from django.apps import AppConfig
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured

from gdaps import require_app


class DrfConfig(AppConfig):
    name = "gdaps.drf"

    def ready(self):

        require_app(self, "rest_framework")
