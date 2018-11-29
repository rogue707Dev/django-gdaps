
import pytest

from gdaps import Interface, PluginError, implements, ExtensionPoint
from .interfaces import ITestInterface1, ITestInterface2, TestPlugin


@implements(ITestInterface1)
class TestPlugin1(TestPlugin):
    pass


with pytest.raises(PluginError):
    @implements(ITestInterface2)
    class TestPlugin2(TestPlugin):
        def get_item(self):
            return "something"

        # does not implement required_method()
        # this must raise an error at declaration time!


@implements(ITestInterface1)
class TestPlugin3(TestPlugin):
    pass


def test_try_instanciate_interface():
    """Try to instantiate an interface directly. Should be forbidden"""
    with pytest.raises(PluginError):
        Interface()


def test_dont_implement_interface_directly():
    """Try to implement an interface directly. Should be forbidden"""
    with pytest.raises(PluginError):
        @implements(Interface)
        class Dummy:
            pass


def test_iterable_extensionpoint():
    """raises an Error if ITestInterface1 is not iterable:"""
    ep = ExtensionPoint(ITestInterface1)
    for plugin in ep:
        pass

    # make sure that it iterates over the right classes
    assert TestPlugin1 in ep
    assert TestPlugin3 in ep


def test_call_method():
    """Raises an error if the implemented method is not callable"""
    ep = ExtensionPoint(ITestInterface2)
    for i in ep:
        dummy = i().get_item()
