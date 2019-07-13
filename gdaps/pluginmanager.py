import os

import logging
import importlib

from django.apps import apps, AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from pkg_resources import iter_entry_points
from typing import List

from gdaps.exceptions import PluginError

__all__ = ["PluginManager"]

logger = logging.getLogger(__name__)


# with Python 3.7 we could use this instead of a plugin_spec dict:
#
# @dataclass
# class PluginSpec:
#     name: str
#     app_name: str
#     verbose_name: str
#     description: str
#     vendor: str
#     version: semver.VersionInfo
#     core_compat_version: semver.VersionInfo
#     author: str
#     author_email: str
#     category: str = "Misc"
#     enabled: bool = True
#     dependencies: list = ['core']


# class Singleton(type):
#     """A Metaclass implementing the Singleton pattern.
#
#     This class is for internal use only
#     """
#
#     _instances = {}
#
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]


class PluginManager:
    """A Generic Django Plugin Manager that finds Django app plugins in a
    plugins folder or setuptools entry points and loads them dynamically.

    It provides a couple of methods to interaft with plugins, load submodules of all available plugins
    dynamically, or get a list of enabled plugins.
    Don't instantiate a ``PluginManager`` directly, just use its static and class methods directly.
    """

    group = ""

    def __init__(self):
        raise PluginError("PluginManager is not meant to be instantiated.")

    @classmethod
    def plugin_path(cls):
        """Returns the absolute path where application plugins live.

        This is basically the Django root + the dotted entry point.
        CAVE: this is not callable from within the settings.py file.
        """
        if cls.group == "":
            raise ImproperlyConfigured(
                "Plugin path could not be determinded. Please run PluginManager.find_plugins() in your settings.py first."
            )
        return os.path.join(settings.BASE_DIR, *cls.group.split("."))

    @classmethod
    def find_plugins(cls, group: str) -> List[str]:
        """Finds plugins from setuptools entry points.

        This function is supposed to be called in settings.py after the
        INSTALLED_APPS variable. Therefore it can not use global variables from
        settings, to prevent circle imports.

        :param group: a dotted path where to find plugin apps. This is used as
            'group' for setuptools' entry points.
        :returns: A list of dotted app_names, which can be appended to
            INSTALLED_APPS.
        """
        if not group:
            raise PluginError(
                "You have to specify an entry points group "
                "where GDAPS can look for plugins."
            )

        cls.group = group

        installed_plugin_apps = []
        for entry_point in iter_entry_points(group=group, name=None):
            appname = entry_point.module_name
            if entry_point.attrs:
                # FIXME: adding an AppConfig does not work yet
                appname += "." + ".".join(entry_point.attrs)

            installed_plugin_apps.append(appname)
            logger.info("Found plugin '{}'.".format(appname))

        return installed_plugin_apps

    @staticmethod
    def plugins(skip_disabled: bool = False) -> List[AppConfig]:
        """Returns a list of AppConfig classes that are GDAPS plugins.

        This method basically checks for the presence of a ``PluginMeta`` class
        within the AppConfig of all apps and returns a list of them.
        :param skip_disabled: If True, skips disabled plugins and only returns enabled ones. Defaults to ``False``.
        """

        # TODO: test plugins() method
        list = []
        for app in apps.get_app_configs():
            if not hasattr(app, "PluginMeta"):
                continue
            if skip_disabled:
                # skip disabled plugins per default
                if not getattr(app.PluginMeta, "enabled", "True"):
                    continue
            list.append(app)

        return list

    @classmethod
    def load_plugin_submodule(cls, submodule: str, mandatory=False) -> list:
        """
        Search plugin apps for specific submodules and load them.

        :param submodule: the dotted name of the Django app's submodule to
            import. This package must be a submodule of the
            plugin's namespace, e.g. "schema" - then
            ["<main>.core.schema", "<main>.laboratory.schema"] etc. will be
            found and imported.
        :param mandatory: If set to True, each found plugin _must_ contain the given
            submodule. If any installed plugin doesn't have it, a PluginError is raised.
        :return: a list of module objects that have been successfully imported.
        """
        modules = []
        importlib.invalidate_caches()
        for app in PluginManager.plugins():

            # import all the submodules from all plugin apps
            from gdaps.conf import gdaps_settings

            dotted_name = "%s.%s" % (app.name, submodule)
            try:
                module = importlib.import_module(dotted_name)
                logger.info("Successfully loaded submodule {}".format(dotted_name))
                modules.append(module)
                logger.info("Loading plugin {}".format(dotted_name))
            except ImportError as e:
                if mandatory:
                    raise PluginError(
                        "The '{plugin_name}' app does not contain a (mandatory) '{module}' module".format(
                            module=submodule, plugin_name=app.name
                        )
                    )
                # ignore non-existing <submodule>.py files
                # in plugins
                logger.error(
                    "Error loading submodule '{}':\n   {}".format(dotted_name, e)
                )
        return modules

    @staticmethod
    def urlpatterns() -> list:
        """Loads all plugins' urls.py and collects their urlpatterns.

        This is maybe not the best approach, but it allows plugins to
        have "global" URLs, and not only namespaced, and it is flexible

        :returns: a list of urlpatterns that can be merged with the global
                  urls.urlpattern."""

        # FIXME: the order the plugins are loaded is not deterministic. This can lead to serious problems,
        # as apps could use the same URL namespace, and depending on which one was loaded first, it may mask the other
        # URL. This has to be fixed.
        #
        # Another unmanaged problem is 'dependencies':
        # FIXME: a dependency manager must be implemented into the PluginManager

        # if gdaps.drf or gdaps.frontend is installed, use their urlpatterns automatically
        module_list = PluginManager.load_plugin_submodule("urls")

        if "gdaps.frontend" in [app.name for app in apps.get_app_configs()]:
            from gdaps.frontend import urls

            module_list += [urls]

        urlpatterns = []
        for module in module_list:
            pattern = getattr(module, "urlpatterns", None)
            if pattern:
                logger.info(
                    "Added urlpatterns from module '{}' to global list.".format(
                        module.__name__
                    )
                )
                urlpatterns += pattern

        return urlpatterns
