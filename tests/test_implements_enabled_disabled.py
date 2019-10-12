from gdaps import Interface, PluginError


@Interface
class ITestInterface:
    pass


class EnabledPlugin(ITestInterface):
    enabled = True


class AutoEnabledPlugin(ITestInterface):
    pass


class DisabledPlugin(ITestInterface):
    enabled = False


def test_enabled_implementations():

    assert len(ITestInterface) == 3
    for i in ITestInterface:
        # either plugins have .enabled=True, or (per default) are enabled by
        # not having this attr.
        # There may not be any disabled plugin in the list!
        assert not hasattr(i, "enabled") or i.enabled


def test_disabled_implementations():

    assert len(ITestInterface) == 3
    for i in ITestInterface.all_plugins():
        # either plugins have .enabled=True, or (per default) are enabled by
        # not having this attr.
        # There may not be any disabled plugin in the list!
        assert hasattr(i, "enabled") and not i.enabled


# ------------------------------------------------------------


@Interface
class INoop2:
    pass


class Baz2(INoop2):
    enabled = False


def test_disabled_implementations():

    for i in INoop2:
        raise PluginError("Disabled extension was returned in Interface!")
