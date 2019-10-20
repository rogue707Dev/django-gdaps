from django.apps import AppConfig


class Plugin1Meta:
    verbose_name = "Plugin 1"
    version = "0.0.1"


class Plugin1Config(AppConfig):

    name = "tests.plugins.plugin1"
    PluginMeta = Plugin1Meta
