import logging
from typing import List, Type

from gdaps.exceptions import PluginError

__all__ = ["Interface", "implements", "ExtensionPoint"]  # "IPlugin", "Plugin"
__version__ = "0.3.9"

default_app_config = "gdaps.apps.GdapsConfig"

logger = logging.getLogger(__name__)


class InterfaceMeta(type):
    """Metaclass for Interface.

    This class assigns a new empty implementations and permissions list to each
    Interface at creation time.
    """

    def __new__(mcs, name, bases, dct):
        """Creates a new Interface class"""

        interface = type.__new__(mcs, name, bases, dct)
        interface._implementations = []
        interface._permissions = []
        return interface

    # def __iter__(mcs):
    #     """Makes Interface iterable."""
    #     return iter(mcs._implementations)


class Interface(metaclass=InterfaceMeta):
    """Base class for interface definitions.

    Inherit from *Interface* and eventually add methods to that class:

    .. code-block:: python

        class IMyInterface(Interface):

            def do_something(self):
                pass

    You can choose whatever name you want for your interfaces, but we recommend you start the name with a capital "I".
    Read more about interfaces in the :ref:`Interfaces` section.
    """

    class Meta:
        pass

    def __new__(cls, *args, **kwargs):
        raise PluginError(
            "<Interface> can't be instantiated directly".format(cls.__class__.__name__)
        )

    @classmethod
    def _is_service(cls):
        """Returns True if Interface describes a "service".

        Services are Interfaces whose implementations are instantiated at creation time.
        Per default, service == true, if not set otherwise at declaration in the Interfaces'
        Meta class.
        """
        return getattr(cls.Meta, "service", True)


class ExtensionPoint:
    """Marker class for Extension points in plugins.

    You can iterate over 'Extensionpoint's via ``for..in``:

    .. code-block:: python

        ep = ExtensionPoint(IMyInterface)
        for plugin in ep:
            plugin.do_something()
    """

    # shamelessly copied (and adapted) from PyUtilib

    def __init__(self, interface: Type[Interface]) -> None:
        """Creates the extension point.

        :param interface: The interface that is referred to.
        """

        if interface is None:
            raise PluginError(
                "An <ExtensionPoint> must point to an <Interface>. Please specify one."
            )
        if interface is Interface:
            raise PluginError(
                "An extension point can't directly refer to <Interface>. Use an <Interface> subclass."
            )
        self._interface = interface
        self.__doc__ = "List of plugins that implement %s" % interface.__name__

    def __iter__(self):
        """Returns an iterator to a set of plugins that match the interface of this extension point."""

        return self.extensions().__iter__()

    def __len__(self):
        """Return the number of plugins that match the interface of this extension point."""
        return len(self.extensions())

    def __contains__(self, cls: type) -> bool:
        """Returns True if this ExtensionPoint contains an object (class or instance) that matches the given class."""
        if self._interface._is_service():
            return cls in [type(impl) for impl in self._interface._implementations]
        else:
            return cls in self._interface._implementations

    def extensions(self) -> set:
        """Returns a set of plugin instances that match the interface of this extension point."""
        ext_set = set()
        for impl in self._interface._implementations:
            # either look for the 'enabled' attribute and just return the plugin, when it's enabled,...
            if hasattr(impl, "enabled"):
                if impl.enabled:
                    ext_set.add(impl)
            else:
                # ...or, if there is no 'enabled' attribute, ignore it and just return the plugin
                ext_set.add(impl)
        return ext_set

    def __repr__(self):
        """Returns a textual representation of the extension point."""
        return "<ExtensionPoint '%s'>" % self._interface.__name__


class Implements:
    """Decorator class for implementing interfaces.

    Just decorate a class:

     .. code-block:: python

        @implements(IMyInterface)
        class PluginA:

            def do_something(self):
                print("Greetings from PluginA")


    You can also implement more than one interface: *@implements(InterfaceA, InterfaceB)* and implement all their
    methods.

    Read more about implementations in the :ref:`Implementations` section.

    """

    def __init__(self, *interfaces: List[Interface]) -> None:  # singleton: bool = True
        """Called at declaration of the decorator (with following class).
        :param interfaces: list of interface classes the decorated class will
                be implementing.
        # :param singleton: if True the implementations will get instanciated immediately, and prevented from
        #         a second instantiation.
        """
        # memoize a list of *Interface*s the decorated class is going to implement
        self._interfaces = []  # type: List[Interface]
        # self._singleton = singleton

        if not interfaces:
            raise PluginError(
                "You have to specify an <Interface> to the @implements decorator."
            )
        for interface in interfaces:
            if interface is Interface:
                raise PluginError(
                    "You can't directly implement <Interface>."
                    "Please subclass <Interface> and use that"
                    "class as parameter for @implements()."
                )

            self._interfaces.append(interface)

    def __call__(self, cls) -> object:
        """Called at decoration time
        :param cls: decorated class
        """
        # add the decorated class to each Interface's internal implementation list
        assert isinstance(cls, type)
        # if cls.Meta.singleton:
        #     # instantiate class immediately if Interface has a singleton marker
        #     cls = cls()
        #     cls._singleton_instance = cls
        # else:
        #     cls._singleton_instance = None

        for interface in self._interfaces:  # type: Interface
            # for attr in [m for m in dir(interface) if not m.startswith("_")]:
            #     # test if implementation implements all methods
            #     if callable(getattr(interface, attr)) and not hasattr(cls, attr):
            #         raise PluginError(
            #             "Class '%s' does not implement method '%s' of Interface '%s'"
            #             % (cls.__name__, attr, interface.__name__)
            #         )
            #     # test if implementation implements all attributes
            #     if not hasattr(cls, attr):
            #         raise PluginError(
            #             "Class '%s' does not implement attribute '%s' of Interface '%s'"
            #             % (cls.__name__, attr, interface.__name__)
            #         )

            # if Interface requires a service, ...
            if interface._is_service():
                # ...directly instantiate a class and save it,
                interface._implementations.append(cls())
            else:
                # ...else save just the class.
                interface._implementations.append(cls)

        return cls


implements = Implements


# class IPlugin(Interface):
#     """A basic interface that provides some useful methods for plugin interaction."""
#
#     def enable(self):
#         pass
#
#     def disable(self):
#         pass
#
#     def enabled(self):
#         pass
#
#
# @implements(IPlugin)
# class Plugin:
#     __enabled__ = True
#
#     def enable(self):
#         self.__enabled__ = True
#
#     def disable(self):
#         self.__enabled__ = False
#
#     def enabled(self):
#         return self.__enabled__
