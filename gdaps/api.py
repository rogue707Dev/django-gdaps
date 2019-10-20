# this is the API of GDAPS itself.
import sys

from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

from gdaps import Interface


@Interface
class IGdapsPlugin:
    def plugin_synchronized(self, app):
        """Called when a plugin is synchronized to database"""



