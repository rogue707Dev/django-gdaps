import pytest

from gdaps import Interface, PluginError


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


class TestPlugin:
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


# Test implementations


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


# Tests


def test_iterable_extensionpoint():
    """Raises an Error if an extension point is not iterable"""
    for _plugin in ITestInterface1:
        pass


# def test_call_method():
#    """Raises an error if an implemented method is not callable"""
#
#    for i in ITestInterface2:
#        _dummy = i.get_item()


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
