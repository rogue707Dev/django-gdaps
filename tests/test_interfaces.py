
import pytest

from gdaps import Interface, PluginError, implements
from tests.interfaces import ITestInterface1, ITestInterface2, TestPlugin


@implements(ITestInterface1)
class TestPlugin1(TestPlugin):
    pass


@implements(ITestInterface2)
class TestPlugin2(TestPlugin):
    def get_item(self):
        return "something"


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


def test_iterable():
    # raises an Error if ITestInterface1 is not iterable:
    for plugin in ITestInterface1:
        pass

    # make sure that it iterates over the right classes
    assert TestPlugin1 in ITestInterface1
    assert TestPlugin3 in ITestInterface1
