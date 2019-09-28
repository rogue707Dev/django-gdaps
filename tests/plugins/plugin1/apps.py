from gdaps.apps import PluginConfig


class Plugin1Meta:
    verbose_name = "Plugin 1"
    version = "0.0.1"


class Plugin1Config(PluginConfig):

    name = "tests.plugins.plugin1"
    pluginMeta = Plugin1Meta
