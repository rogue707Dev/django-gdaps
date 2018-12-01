import pytest

from gdaps import ExtensionPoint, Interface, PluginError, implements
from .interfaces import ITestInterface1, ITestInterface2
from .test_interfaces import TestPlugin1, TestPlugin3


# Test classes for interfaces and their implementations
class ITestInterface3(Interface):
    pass


class ITestInterface4(Interface):
    pass


@implements(ITestInterface3)
class Foo:
    pass


@implements(ITestInterface4)
class Bar:
    pass


@implements(ITestInterface4)
class Baz:
    pass

class ITestInterface5(Interface):
    pass


def test_empty_ep():
    """Tests if Creating an extension point without an Interface fails"""

    with pytest.raises(PluginError):
        ep = ExtensionPoint(None)


def test_iterable_extensionpoint():
    """Raises an Error if an extension point is not iterable"""
    ep = ExtensionPoint(ITestInterface1)
    for plugin in ep:
        pass

    # make sure that it iterates over the right classes
    assert TestPlugin1 in ep
    assert TestPlugin3 in ep


def test_call_method():
    """Raises an error if an implemented method is not callable"""
    ep = ExtensionPoint(ITestInterface2)
    for i in ep():
        dummy = i().get_item()


def test_direct_interface_extension():
    """Tests if direct implementation of "Interface" fails"""

    with pytest.raises(PluginError):
        ep = ExtensionPoint(Interface)

    # This should pass
    ep = ExtensionPoint(ITestInterface2)

def test_ep_repr():
    ep = ExtensionPoint(ITestInterface2)
    assert ep.__repr__() == "<ExtensionPoint 'ITestInterface2'>"


def test_ep_len():
    ep = ExtensionPoint(ITestInterface5)
    assert len(ep) == 0

    ep = ExtensionPoint(ITestInterface3)
    assert len(ep) == 1

    ep = ExtensionPoint(ITestInterface4)
    assert len(ep) == 2

