import pytest

from gdaps import implements, Interface, ExtensionPoint, Implements, PluginError


class IFoo(Interface):
    def foo_method(self):
        pass


class IAttribute1(Interface):
    """Implementations should contain a 'foo' attribute: list of str"""

    foo = []


class IFooNonService(Interface):
    class Meta:
        service = False


@implements(IFoo)
class Foo:
    def foo_method(self):
        pass


@implements(IFooNonService)
class Baz1:
    pass


# Tests


def test_nonservice_is_not_instantiated():
    ep = ExtensionPoint(IFooNonService)
    for i in ep:
        assert i is Baz1


def test_interface_attribute():
    ep = ExtensionPoint(IFoo)

    assert hasattr(ep, "_interface")


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


# def test_attribute_missing():
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
