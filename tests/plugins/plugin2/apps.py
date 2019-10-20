from django.apps import AppConfig


class Plugin1Meta:
    verbose_name = "Plugin 2"
    version = "blah_foo"


class Plugin2Config(AppConfig):

    name = "tests.plugins.plugin2"
    PluginMeta = Plugin1Meta
