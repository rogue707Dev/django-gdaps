from gdaps import Interface, PluginError, implements, ExtensionPoint
from .plugins import FirstInterface


def test_plugin1():
    ep = ExtensionPoint(FirstInterface)
    for plugin in ep:
        assert plugin.first_method() == "first"
