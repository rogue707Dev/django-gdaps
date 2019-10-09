from gdaps import Interface, PluginError


@Interface
class INoop:
    pass


class Baz(INoop):
    enabled = True


class Bar(INoop):
    pass


def test_enabled_implementations():

    assert len(INoop) == 2
    for i in INoop:
        # either plugins have .enabled=True, or (per default) are enabled by
        # not having this attr
        assert not hasattr(i, "enabled") or i.enabled


# ------------------------------------------------------------


@Interface
class INoop2:
    pass


class Baz2(INoop2):
    enabled = False


def test_disabled_implementations():

    for i in INoop2:
        raise PluginError("Disabled extension was returned in Interface!")
