from gdaps.pluginmanager import PluginManager


def test_pluginmanager_findplugins_empty():
    assert PluginManager.find_plugins("gdapstest_foo786578645786.plugins") == []
