import pytest

from gdaps import ExtensionPoint, Interface, PluginError, implements


class ITestInterface1(Interface):
    pass


class ITestInterface2(Interface):
    def required_method(self):
        pass

    def get_item(self):
        pass


class INonService(Interface):
    class Meta:
        service = False

    def foo(self):
        pass


@implements(INonService)
class NonService1:
    def foo(self):
        pass


@implements(INonService)
class NonService2:
    def foo(self):
        pass


class TestPlugin:
    pass


# Test classes for interfaces and their implementations
class ITestInterface3(Interface):
    pass


class ITestInterface4(Interface):
    pass


class ITestInterface5(Interface):
    pass


class IAttribute1Interface(Interface):
    """Implementations should contain a 'foo' attribute: list of str"""

    foo = []


# Test implementations


@implements(ITestInterface3)
class Foo:
    pass


@implements(ITestInterface4)
class Bar:
    pass


@implements(ITestInterface4)
class Baz:
    pass


@implements(IAttribute1Interface)
class Attribute2Class:
    foo = ["first", "second"]


@implements(ITestInterface1)
class TestPlugin1(TestPlugin):
    pass


@implements(ITestInterface1)
class TestPlugin3(TestPlugin):
    pass


# Tests


def test_empty_ep():
    """Tests if Creating an extension point without an Interface fails"""

    with pytest.raises(PluginError):
        _ep = ExtensionPoint(None)


def test_iterable_extensionpoint():
    """Raises an Error if an extension point is not iterable"""
    ep = ExtensionPoint(ITestInterface1)
    for _plugin in ep:
        pass


#def test_call_method():
#    """Raises an error if an implemented method is not callable"""
#
#    ep = ExtensionPoint(ITestInterface2)
#    for i in ep():
#        _dummy = i().get_item()


def test_direct_interface_extension():
    """Tests if direct implementation of "Interface" fails"""

    with pytest.raises(PluginError):
        _ep = ExtensionPoint(Interface)

    # This should pass
    _ep = ExtensionPoint(ITestInterface2)


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


def test_attribute():
    # directly instantiate a class, which should contain an attribute.
    a = Attribute2Class()
    assert a.foo == ["first", "second"]


def test_nonservice_plugins():
    ep = ExtensionPoint(INonService)
    for i in ep:
        # compare classes, not instances
        assert NonService1 in ep
        assert NonService2 in ep

        # don't accept arbitrary instances as comparison objects
        assert NonService1() not in ep

        # methods cannot be called, as there is no instance yet
        with pytest.raises(TypeError):
            i.foo()

        i().foo()

