import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import call_command

from gdaps import ExtensionPoint
from gdaps.models import GdapsPlugin
from gdaps.pluginmanager import PluginManager
from .plugins import FirstInterface


def test_plugin1():
    ep = ExtensionPoint(FirstInterface)
    assert len(ep) != 0
    for plugin in ep:
        assert plugin.first_method() == "first"


def test_plugin_meta():
    from django.apps import apps

    apps = PluginManager.plugins()
    assert len(apps) != 0
    for app_config in PluginManager.plugins():
        meta = app_config.PluginMeta
        assert meta.verbose_name == "Plugin 1"


@pytest.mark.django_db
def test_plugin_initialize_cmd():

    # first, no plugins are installed.
    with pytest.raises(ObjectDoesNotExist):
        GdapsPlugin.objects.get(name="tests.plugins.plugin1")

    # second, initialize plugins
    call_command("initializeplugins")

    # third, now all plugins must be installed
    plugin1 = GdapsPlugin.objects.get(name="tests.plugins.plugin1")
    assert plugin1.name == "tests.plugins.plugin1"
    assert plugin1.version == "0.0.1"
    assert plugin1.verbose_name == "Plugin 1"
