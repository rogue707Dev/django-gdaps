import logging
import typing
from typing import Iterable

from django.apps import AppConfig

from gdaps.exceptions import PluginError


__all__ = ["Interface", "require_app"]
__version__ = "0.4.2"

default_app_config = "gdaps.apps.GdapsConfig"

logger = logging.getLogger(__name__)


class InterfaceMeta(type):
    """Metaclass of Interfaces and Implementations

    This class follows Marty Alchin's principle of MountPoints, thanks for his GREAT piece of software:
    http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    """

    def __new__(mcs, name, bases, dct):
        """Creates a new Interface class"""

        cls = type.__new__(mcs, name, bases, dct)
        if mcs == "Interface":
            raise PluginError(
                "Interfaces must not be implemented directly. Please subclass "
                "<Interface> and implement that interface by subclassing it again."
            )
        return cls

    def __init__(cls, name, bases, dct) -> None:

        if not hasattr(cls, "_implementations"):
            # This branch only executes when processing the interface itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls._implementations = []
            cls.__interface__ = True
        else:
            cls.___interface__ = False
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            service = getattr(cls, "__service__", True)
            if service:
                plugin = cls()
            else:
                plugin = cls

            for base in bases:
                # if hasattr(base, "___interface__"):
                # if getattr(base, "__service__", True) == service:
                if hasattr(base, "_implementations"):
                    base._implementations.append(plugin)
                # else:
                #     raise PluginError(
                #         "A Plugin can't implement service AND non-service "
                #         "interfaces at the same time. "
                #     )

    def __iter__(mcs) -> typing.Iterable:
        return iter(
            # return only enabled plugins
            impl
            for impl in mcs._implementations
            if getattr(impl, "enabled", True)
        )

    def all_plugins(cls) -> Iterable:
        return iter(cls._implementations)

    def __len__(self) -> int:
        """Return the number of plugins that implement this interface."""
        return len(self._implementations)

    def __contains__(self, cls: type) -> bool:
        """Returns True if there is a plugin implementing this interface."""
        # TODO: test
        if getattr(self, "__service__", True):
            return cls in [type(impl) for impl in self._implementations]
        else:
            return cls in self._implementations

    def __repr__(self) -> str:
        """Returns a textual representation of the interface/implementation."""
        # FIXME: fix repr of Interfaces
        if getattr(self, "___interface__", False):
            return f"<Interface '{self.__name__}'>"
        else:
            return f"<Implementation '{self.__name__}' of {self.__class__}'>"


# noinspection PyPep8Naming
def Interface(cls):
    """Decorator for classes that are interfaces.

    Declare an interface using the ``@Interface`` decorator, optionally add add attributes/methods to that class:

        .. code-block:: python

            @Interface
            class IFooInterface:
                def do_something(self):
                    pass

        You can choose whatever name you want for your interfaces, but we recommend you start the name with a capital "I".
        Read more about interfaces in the :ref:`Interfaces` section."""
    if type(cls) != type:
        raise TypeError(f"@Interface must decorate a class, not {type(cls)}")
    interface_meta = InterfaceMeta(cls.__name__, cls.__bases__, dict(cls.__dict__))
    return interface_meta


def require_app(appconfig: AppConfig, required_app_name: str) -> None:
    """Helper function for AppConfig.ready - checks if an app is installed.

    An ``ImproperlyConfigured`` Exception is raised if the required app is not present.

    :param appconfig: the AppConfig which requires another app. usually use ``self`` here.
    :param required_app_name: the required app name.
    """
    from django.apps import apps
    from django.core.exceptions import ImproperlyConfigured

    if appconfig.name not in [app.name for app in apps.get_app_configs()]:
        raise ImproperlyConfigured(
            "The '{}' module relies on {}. Please add '{}' to your INSTALLED_APPS.".format(
                appconfig.name, appconfig.verbose_name, required_app_name
            )
        )
