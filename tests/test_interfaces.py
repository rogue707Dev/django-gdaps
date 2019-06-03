import pytest

from gdaps import Interface, implements, ExtensionPoint
from gdaps.exceptions import PluginError


class ITestInterface1(Interface):
    pass


class ITestInterface2(Interface):
    def required_method(self):
        pass

    def get_item(self):
        pass


class TestPlugin:
    pass


@implements(ITestInterface1)
class TestPlugin1(TestPlugin):
    pass


@implements(ITestInterface1)
class TestPlugin3(TestPlugin):
    pass


# def test_missing_method():
#     with pytest.raises(PluginError):
#
#         @implements(ITestInterface2)
#         class TestPlugin2(TestPlugin):
#             # does not implement required_method()
#             # this must raise an error at declaration time!
#             def get_item(self):
#                 return "something"


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


def test_multiple_interfaces():
    """Try to implement more than one interfaces in one implementation"""

    @implements(ITestInterface1, ITestInterface2)
    class Dummy:
        def required_method(self):
            pass

        def get_item(self):
            pass

    ep1 = ExtensionPoint(ITestInterface1)
    assert Dummy in ep1

    ep2 = ExtensionPoint(ITestInterface2)
    assert Dummy in ep2
