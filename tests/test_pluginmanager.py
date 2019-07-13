from gdaps.pluginmanager import PluginManager


def test_pluginmanager_findplugins_empty():
    # try to find plugins from a nonexisting entry point
    assert PluginManager.find_plugins("gdapstest_foo786578645786.plugins") == []
