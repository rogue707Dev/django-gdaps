import pytest

from gdaps import Interface, InterfaceMeta


@Interface
class IEmptyInterface:
    pass


@Interface
class IEmptyInterface2:
    pass


@Interface
class ICount3Interface:
    pass


class CountImpl1(ICount3Interface):
    pass


class CountImpl2(ICount3Interface):
    pass


class CountImpl3(ICount3Interface):
    pass


@Interface
class ITestInterfacwWith2Methods:
    def required_method(self):
        pass

    def get_item(self):
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


class ChildClassPlugin1(TestPlugin, IEmptyInterface):
    pass


class ChildClassPlugin2(TestPlugin, IEmptyInterface2):
    pass


# def test_missing_attribute():
#    with pytest.raises(PluginError):
#
#        class MissingAttr(IAttribute1):
#            pass

# def test_missing_method():
#     with pytest.raises(PluginError):
#
#         class TestPlugin2(TestPlugin, ITestInterface2):
#             # does not implement required_method()
#             # this must raise an error at declaration time!
#             def get_item(self):
#                 return "something"


def test_dont_instanciate_interface():
    """Try to instantiate an interface directly. Should be forbidden"""
    with pytest.raises(TypeError):
        Interface()


def test_dont_implement_interface_directly():
    """Try to implement an "Interface" directly. Should be forbidden"""
    with pytest.raises(TypeError):

        class Dummy(Interface):
            pass


def test_class_implementing_2_interfaces():
    """Try to implement more than one interfaces in one implementation"""

    class Dummy(IEmptyInterface, ITestInterfacwWith2Methods):
        def required_method(self):
            pass

        def get_item(self):
            pass

    assert Dummy in IEmptyInterface
    assert Dummy in ITestInterfacwWith2Methods


def test_class_implementing_3_interfaces():
    """Try to implement more than one interfaces in one implementation"""

    class Dummy(IEmptyInterface, IEmptyInterface2, ITestInterfacwWith2Methods):
        def required_method(self):
            pass

        def get_item(self):
            pass

    assert Dummy in IEmptyInterface
    assert Dummy in IEmptyInterface2
    assert Dummy in ITestInterfacwWith2Methods


def test_class_inheriting_class_and_implementing_interface():
    """Try to implement more than one interfaces in one implementation"""

    class Dummy(ChildClassPlugin1, IEmptyInterface2):
        pass

    assert Dummy in IEmptyInterface
    assert Dummy in IEmptyInterface2


def test_interface_implementations_attr():
    """tests if _implementations attribute is existing and accessible"""
    # FIXME: protected members should not be accessed...
    assert hasattr(IEmptyInterface, "_implementations")
    assert hasattr(ITestInterfacwWith2Methods, "_implementations")


def test_iterable_interface():
    """Raises an Error if an extension point is not iterable"""
    iter(IEmptyInterface)


def test_call_method():
    """Raises an error if an implemented method is not callable"""

    for i in ITestInterfacwWith2Methods:
        _dummy = i.get_item()


def test_direct_interface_extension():
    """Tests if direct implementation of "Interface" fails"""

    with pytest.raises(TypeError):
        for _plugin in Interface:
            pass

    # This should pass
    for _plugin in ITestInterfacwWith2Methods:
        pass


def test_count_implementations():
    assert len(ICount3Interface._implementations) == 3


def test_ep_len():
    """tests countability of plugins via interface"""
    assert len(ITestInterface5) == 0

    assert len(ITestInterface3) == 1

    assert len(ITestInterface4) == 2


def test_attribute():
    # directly instantiate a class, which should contain an attribute.
    a = Attribute2Class()
    assert a.foo == ["first", "second"]


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
