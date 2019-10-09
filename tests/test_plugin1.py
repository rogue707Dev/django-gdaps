import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command

from gdaps.models import GdapsPlugin
from gdaps.pluginmanager import PluginManager
from .plugins import FirstInterface


def test_plugin1():
    assert len(FirstInterface) != 0
    for plugin in FirstInterface:
        assert plugin.first_method() == "first"


def test_plugin_meta():
    from django.apps import apps

    apps = PluginManager.plugins()
    assert len(apps) != 0
    for app_config in apps:
        assert hasattr(app_config.PluginMeta, "verbose_name")
        assert hasattr(app_config.PluginMeta, "version")


@pytest.mark.django_db
def test_plugin_initialize_cmd():

    # first, no plugins are installed.
    with pytest.raises(ObjectDoesNotExist):
        # noinspection PyUnresolvedReferences
        GdapsPlugin.objects.get(name="tests.plugins.plugin1")

    # second, initialize plugins
    call_command("initializeplugins")

    # third, now all plugins must be installed
    # noinspection PyUnresolvedReferences
    plugin1 = GdapsPlugin.objects.get(name="tests.plugins.plugin1")
    assert plugin1.name == "tests.plugins.plugin1"
    assert plugin1.version == "0.0.1"
    assert plugin1.verbose_name == "Plugin 1"
