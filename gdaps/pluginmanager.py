"""
GDAPS - Generic Django Apps Plugin System
Copyright (C) 2018 Christian González

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import os

import logging
import importlib

from django.apps import apps, AppConfig
from django.conf import settings
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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# TODO: don't use a Singleton here, there are only @classmethods?
# just make sure the PluginManager is never instantiated? Which is better?
class PluginManager(metaclass=Singleton):
    """A Generic Django Plugin Manager that finds Django app plugins in a
    plugins folder or pkg_resources entry points and loads them dynamically.

    It provides methods to load submodules of all available plugins
    dynamically."""

    group = ""

    found_apps = []

    @classmethod
    def plugin_path(cls):
        assert cls.group != ""
        return os.path.join(settings.BASE_DIR, *cls.group.split("."))

    @classmethod
    def find_plugins(cls, group: str) -> List[str]:
        """Finds plugins from setuptools entrypoints

        This function is supposed to be called in settings.py after the
        INSTALLED_APPS variable. Therefore it can not use global variables from
        settings, to prevent circle imports.

        :group: a dotted path where wo find plugin apps. This is used as
            'group' for setuptools' entry points.
        :returns: A list of dotted app_names, which can be appended to
            INSTALLED_MODULES.
        """
        if not group:
            raise PluginError(
                "You have to specify an entry points group "
                "where GDAPS can look for plugins."
            )

        cls.group = group
        found_apps = []

        for entry_point in iter_entry_points(group=group, name=None):
            appname = entry_point.module_name
            if entry_point.attrs:
                # FIXME: adding an AppConfig does not work yet
                appname += "." + ".".join(entry_point.attrs)

            found_apps.append(appname)
            logger.info("Found plugin '{}', adding to INSTALLED_APPS.".format(appname))

        # save a relative import path for plugins, derived from the "group" dotted plugin path
        # cls.plugin_path = os.path.join(*cls.group.split("."))

        cls.found_apps = found_apps
        return found_apps

    @classmethod
    def plugins(cls) -> List[str]:
        # TODO: test plugins() method
        """Returns a list of installed plugin apps, either set in INSTALLED_APPS directly, or found via entrypoint"""
        for app in apps.get_app_configs():
            from gdaps.conf import gdaps_settings

            try:
                if app.name.startswith(cls.group) and app.name not in cls.found_apps:
                    cls.found_apps += [app.name]
            except ValueError:
                pass
        # TODO: should we return a copy [:] of the list here?
        return cls.found_apps

    @classmethod
    def load_plugin_submodule(cls, submodule: str) -> list:
        """
        Search plugin apps for specific submodules and load them.

        :param submodule: the dotted name of the Django app's submodule to
            import. This package must be a submodule of the
            plugin's namespace, e.g. "schema" - then
            ["<main>.core.schema", "<main>.laboratory.schema"] etc. will be
            found and imported.
        :return: a list of module objects that have been successfully imported.
        """
        modules = []
        importlib.invalidate_caches()
        for app_name in PluginManager.plugins():

            # import all the subbodules from all plugin apps
            from gdaps.conf import gdaps_settings

            if app_name.startswith(cls.group):

                dotted_name = "%s.%s" % (app_name, submodule)
                try:
                    module = importlib.import_module(dotted_name)
                    logger.info("Successfully loaded submodule {}".format(dotted_name))
                    modules.append(module)
                    logger.info("Loading plugin {}".format(dotted_name))
                except ImportError as e:
                    # ignore non-existing <submodule>.py files
                    # in plugins
                    logger.error(
                        "Error loading submodule '{}':\n   {}".format(dotted_name, e)
                    )
        return modules

    @staticmethod
    def populate_apps(new_apps: list) -> None:
        """This is a more or less copy of django.apps.Apps().populate(),
        as the original version refuses to do anything if apps.ready==True
        and returns. So we copy the behaviour here to mimic an app reloading.

        This is not ideal, but until Django "fixes" this issue of dynamic
        app reloading (https://code.djangoproject.com/ticket/29554)
        it's the best we could do.
        :param new_apps: a list of dotted app names to load into Django
        """
        new_app_configs = []

        # Phase 1: initialize app configs and import app modules.
        for entry in new_apps:
            if isinstance(entry, AppConfig):
                app_config = entry
            else:
                app_config = AppConfig.create(entry)

            if app_config.label in apps.app_configs:
                return

            apps.ready = False
            apps.apps_ready = False
            apps.models_ready = False

            new_app_configs.append(app_config)

            # add new app name to the global app_configs
            apps.app_configs[app_config.label] = app_config
            app_config.apps = apps

            apps.apps_ready = True

            # Phase 2: import models modules.
            for app_config in new_app_configs:
                app_config.import_models()

            apps.clear_cache()

            apps.models_ready = True

            # Phase 3: run ready() methods of app configs.
            for app_config in new_app_configs:
                app_config.ready()

            apps.ready = True
            logger.debug("Django apps: {}".format(apps.app_configs))

    @staticmethod
    def urlpatterns() -> list:
        """Loads all plugins' urls.py and collects their urlpatterns.

        This is maybe not the best approach, but it allows plugins to
        have "global" URLs, and not only namespaced, and it is flexible

        :returns: a list of urlpatterns that can be merged with the global
        urls.urlpattern.
        """

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
