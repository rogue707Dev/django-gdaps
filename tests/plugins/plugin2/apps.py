from gdaps.apps import PluginConfig


class Plugin2Config(PluginConfig):

    name = "tests.plugins.plugin2"

    class PluginMeta:
        verbose_name = "Plugin 2"
        version = "blah_foo"
