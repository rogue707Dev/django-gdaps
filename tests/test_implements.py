import pytest

from gdaps import implements, Interface, ExtensionPoint, Implements, PluginError


class IFoo(Interface):
    def foo_method(self):
        pass


class IAttribute1(Interface):
    """Implementations should contain a 'foo' attribute: list of str"""

    foo = []


@implements(IFoo)
class Foo:
    def foo_method(self):
        pass


# Tests


# FIXME: does not work yet, see issue #1
def test_service_is_instantiated():
    ep = ExtensionPoint(IFoo)
    for i in ep:
        assert hasattr(i, "foo_method")
        assert isinstance(i, Foo)


def test_service_method_call():
    ep = ExtensionPoint(IFoo)
    for i in ep:
        i.foo_method()


#def test_attribute_missing():
#    with pytest.raises(PluginError):
#
#        @implements(IAttribute1)
#        class MissingAttr:
#            pass


def test_empty_implements():
    with pytest.raises(PluginError):

        @implements()  # implements must have an Interface as argument
        class Foo:
            pass


def test_enabled_implementations():
    class Noop(Interface):
        pass

    @implements(Noop)
    class Baz:
        enabled = True

    @implements(Noop)
    class Bar:
        pass

    ep = ExtensionPoint(Noop)
    assert len(ep) == 2
    for i in ep:
        # either plugins have .enabled=True, or (per default) are enabled by
        # not having this attr
        assert not hasattr(i, "enabled") or i.enabled


def test_disabled_implementations():
    class Noop(Interface):
        pass

    @implements(Noop)
    class Baz:
        enabled = False

    ep = ExtensionPoint(Noop)
    for i in ep:
        raise PluginError("Disabled extension was returned in Extensionpoint!")
