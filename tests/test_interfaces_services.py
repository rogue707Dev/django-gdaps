import pytest

from gdaps import Interface, InterfaceMeta


@Interface
class IService:
    __service__ = True

    def foo(self):
        pass


@Interface
class INonService:
    __service__ = False

    def foo(self):
        pass


@Interface
class INonService2:
    __service__ = False


# Classes/Plugins


class Service(IService):
    pass


class NonService1(INonService):
    def foo(self):
        pass


class NonService2(INonService):
    def foo(self):
        pass


class NonServicePlugin1(INonService2):
    pass


# Tests


def test_nonservice_is_not_instantiated():
    for i in INonService2:
        assert i is NonServicePlugin1


def test_service_is_instantiated():
    assert len(IService) > 0
    for i in IService:
        assert isinstance(i, IService)


def test_service_has_attr_or_method():
    for i in IService:
        assert hasattr(i, "foo")


def test_service_method_callable():
    for i in IService:
        assert callable(i.foo)


def test_service_method_call():
    for i in IService:
        i.foo()


def test_nonservice_plugins():
    for i in INonService:
        # compare classes, not instances
        assert NonService1 in INonService
        assert NonService2 in INonService

        # make sure that there is no instance in the list of plugins, just classes
        for cls in INonService:
            assert type(cls) == InterfaceMeta
            assert not isinstance(cls, INonService)

        # methods cannot be called, as there is no instance yet
        with pytest.raises(TypeError):
            i.foo()

        i().foo()


def test_service_plugins():
    assert len(IService) > 0
    for i in IService:
        # compare classes, not instances
        assert NonService1 in INonService
        assert NonService2 in INonService

        # make sure that there is no instance in the list of plugins, just classes
        for cls in IService:
            assert type(cls) != InterfaceMeta
            assert isinstance(cls, IService)

        # methods cannot be called, as there is no instance yet
        with pytest.raises(TypeError):
            i().foo()

        i.foo()
