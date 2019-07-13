from gdaps.apps import PluginConfig


class Plugin1Config(PluginConfig):

    name = "tests.plugins.plugin1"

    class PluginMeta:
        verbose_name = "Plugin 1"
        version = "0.0.1"

