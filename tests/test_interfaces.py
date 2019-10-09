import pytest

from gdaps import Interface
from gdaps.exceptions import PluginError


@Interface
class ITestInterface1:
    pass


@Interface
class ITestInterface2:
    def required_method(self):
        pass

    def get_item(self):
        pass


class TestPlugin:
    pass


class TestPlugin1(TestPlugin, ITestInterface1):
    pass


class TestPlugin3(TestPlugin, ITestInterface1):
    pass


# def test_missing_method():
#     with pytest.raises(PluginError):
#
#         class TestPlugin2(TestPlugin, ITestInterface2):
#             # does not implement required_method()
#             # this must raise an error at declaration time!
#             def get_item(self):
#                 return "something"


def test_try_instanciate_interface():
    """Try to instantiate an interface directly. Should be forbidden"""
    with pytest.raises(TypeError):
        Interface()


def test_dont_implement_interface_directly():
    """Try to implement an "Interface" directly. Should be forbidden"""
    with pytest.raises(TypeError):

        class Dummy(Interface):
            pass


# FIXME: does not work yet
def test_multiple_interfaces():
    """Try to implement more than one interfaces in one implementation"""

    class Dummy(ITestInterface1, ITestInterface2):
        def required_method(self):
            pass

        def get_item(self):
            pass

    assert Dummy in ITestInterface1
    assert Dummy in ITestInterface2


def test_interface_implementations_attr():

    assert hasattr(ITestInterface1, "_implementations")
    assert len(ITestInterface1._implementations) == 3

    assert hasattr(ITestInterface2, "_implementations")
    assert len(ITestInterface2._implementations) == 1
