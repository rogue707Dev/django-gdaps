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


@Interface
class INonService:
    __service__ = False

    def foo(self):
        pass


class NonService1(INonService):
    def foo(self):
        pass


class NonService2(INonService):
    def foo(self):
        pass


# Test classes for interfaces and their implementations
@Interface
class ITestInterface3:
    pass


@Interface
class ITestInterface4:
    pass


@Interface
class ITestInterface5:
    pass


@Interface
class IAttribute1Interface:
    """Implementations should contain a 'foo' attribute: list of str"""

    foo = []


class TestPlugin:
    pass


class Foo(ITestInterface3):
    pass


class Bar(ITestInterface4):
    pass


class Baz(ITestInterface4):
    pass


class Attribute2Class(IAttribute1Interface):
    foo = ["first", "second"]


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


def test_iterable_interface():
    """Raises an Error if an extension point is not iterable"""
    iter(ITestInterface1)


def test_call_method():
    """Raises an error if an implemented method is not callable"""

    for i in ITestInterface2:
        _dummy = i.get_item()


def test_direct_interface_extension():
    """Tests if direct implementation of "Interface" fails"""

    with pytest.raises(TypeError):
        for _plugin in Interface:
            pass

    # This should pass
    for _plugin in ITestInterface2:
        pass


def test_ep_len():
    assert len(ITestInterface5) == 0

    assert len(ITestInterface3) == 1

    assert len(ITestInterface4) == 2


def test_attribute():
    # directly instantiate a class, which should contain an attribute.
    a = Attribute2Class()
    assert a.foo == ["first", "second"]


def test_nonservice_plugins():
    for i in INonService:
        # compare classes, not instances
        assert NonService1 in INonService
        assert NonService2 in INonService

        # don't accept arbitrary instances as comparison objects
        assert NonService1() not in INonService

        # methods cannot be called, as there is no instance yet
        with pytest.raises(TypeError):
            i.foo()

        i().foo()


def test_interface_called():
    with pytest.raises(TypeError):

        @Interface()  # Interface must not be "called"
        class Foo:
            pass


def test_interface_with_str_argument():
    with pytest.raises(TypeError):

        @Interface("baz")  # Interface must not have an argument
        class Foo:
            pass


def test_interface_with_class_as_argument():
    with pytest.raises(TypeError):

        class Baz:
            pass

        @Interface(Baz)  # Interface must not have an argument
        class Foo:
            pass
