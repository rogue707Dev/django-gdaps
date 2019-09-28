# copied / adapted from Pretix
import gdaps
from gdaps.api import PluginConfig


class GDAPSPluginMeta:
    version = gdaps.__version__
    author = "Christian Gonzalez"
    author_email = "christian.gonzalez@nerdocs.at"
    category = "GDAPS"
    visible = False


class GdapsConfig(PluginConfig):
    name = "gdaps"
    pluginMeta = GDAPSPluginMeta
