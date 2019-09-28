from gdaps import implements, Interface, ExtensionPoint, PluginError


class INoop(Interface):
    pass


@implements(INoop)
class Baz:
    enabled = True


@implements(INoop)
class Bar:
    pass


def test_enabled_implementations():

    ep = ExtensionPoint(INoop)
    assert len(ep) == 2
    for i in ep:
        # either plugins have .enabled=True, or (per default) are enabled by
        # not having this attr
        assert not hasattr(i, "enabled") or i.enabled


# ------------------------------------------------------------


class INoop2(Interface):
    pass


@implements(INoop2)
class Baz:
    enabled = False


def test_disabled_implementations():

    ep = ExtensionPoint(INoop2)
    for i in ep:
        raise PluginError("Disabled extension was returned in Extensionpoint!")
