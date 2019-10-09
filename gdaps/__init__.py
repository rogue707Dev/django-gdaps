import logging
from typing import List, Type

from django.apps import AppConfig

from gdaps.exceptions import PluginError


__all__ = ["Interface", "require_app"]
__version__ = "0.4.0"

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

    def __init__(cls, name: str, bases: dict, dct: dict):

        if not hasattr(cls, "_implementations"):
            # This branch only executes when processing the interface itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls._implementations = []
            cls._interface = True
        else:
            cls._interface = False
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            if getattr(cls, "__service__", True):
                cls._implementations.append(cls())
            else:
                cls._implementations.append(cls)

    def __iter__(mcs):
        # TODO: test
        return iter(
            # return only enabled plugins
            impl
            for impl in mcs._implementations
            if getattr(impl, "enabled", True)
        )

    def __len__(self):
        """Return the number of plugins that implement this interface."""
        # TODO: test
        return len(self._implementations)

    def __contains__(self, cls: type) -> bool:
        """Returns True if there is a plugin implementing this interface."""
        # TODO: test
        if getattr(self, "__service__", True):
            return cls in [type(impl) for impl in self._implementations]
        else:
            return cls in self._implementations

    def __repr__(self):
        """Returns a textual representation of the interface/implementation."""
        if self._interface:
            return f"<Interface '{self.__name__}'>"
        else:
            return f"<Implementation '{self.__name__} of Interface {self.__class__}'>"


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
