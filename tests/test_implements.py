import pytest

from gdaps import Interface, PluginError


@Interface
class IFoo:
    def foo_method(self):
        pass


@Interface
class IAttribute1:
    """Implementations should contain a 'foo' attribute: list of str"""

    foo = []


@Interface
class IFooNonService:
    __service__ = False


class Foo(IFoo):
    def foo_method(self):
        pass


class Baz1(IFooNonService):
    pass


# Tests


def test_nonservice_is_not_instantiated():
    for i in IFooNonService:
        assert i is Baz1


def test_implementations_attribute():
    # FIXME: maybe a test of a "protected" member is not necessary
    assert hasattr(IFoo, "_implementations")


def test_service_is_instantiated():
    for i in IFoo:
        assert hasattr(i, "foo_method")
        assert isinstance(i, Foo)


def test_service_method_call():
    for i in IFoo:
        i.foo_method()


# def test_attribute_missing():
#    with pytest.raises(PluginError):
#
#        class MissingAttr(IAttribute1):
#            pass


def test_empty_implements():
    with pytest.raises(TypeError):

        @Interface()  # Interface must not have an argument
        class Foo:
            pass

        @Interface("baz")  # Interface must not have an argument
        class Foo2:
            pass
