# this is the API of GDAPS itself.
import gdaps
from django.apps import AppConfig


class PluginConfig(AppConfig):
    """Convenience class for GDAPS plugins to inherit from.

    While it is not strictly necessary to inherit from this class - duck typing is ok -
    it simplifies the type suggestions and autocompletion of IDEs like PyCharm, as PluginMeta is already declared here.
    """

    PluginMeta: "GdapsPluginMeta" = None
