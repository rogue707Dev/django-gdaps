from django.test.signals import setting_changed
from gdaps.conf import PluginSettings


# required parameter.
NAMESPACE = "PLUGIN1"

# Optional defaults. Leave empty if not needed.
DEFAULTS = {
    "FOO": 33,
    "INTERFACE": "tests.plugins.plugin1.api.FirstInterface",
    "ARRAY": [1, 2, 3],
    "OVERRIDE": 10,
}

# Optional list of settings that are allowed to be in 'string import' notation. Leave empty if not needed.
# example: 'medux.plugins.fooplugin2.models.FooModel'
IMPORT_STRINGS = "INTERFACE"

# Optional list of settings that have been removed. Leave empty if not needed.
REMOVED_SETTINGS = ()

plugin1_settings = PluginSettings(
    namespace=NAMESPACE,
    defaults=DEFAULTS,
    import_strings=IMPORT_STRINGS,
    removed_settings=REMOVED_SETTINGS,
)


def reload_plugin1_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "FOOPLUGIN2":
        plugin1_settings.reload()


setting_changed.connect(reload_plugin1_settings)
