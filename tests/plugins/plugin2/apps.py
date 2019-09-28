from gdaps.apps import PluginConfig


class PluginMeta:
    verbose_name = "Plugin 2"
    version = "blah_foo"


class Plugin2Config(PluginConfig):

    name = "tests.plugins.plugin2"
    pluginMeta = PluginMeta
