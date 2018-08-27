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
from pkg_resources import iter_entry_points
from typing import List

__all__ = ['PluginManager']

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


class PluginManager(metaclass=Singleton):
    """A Generic Django Plugin Manager that finds Django app plugins in a
    plugins folder or pkg_resources entry points and loads them dynamically.

    It provides methods to load submodules of all available plugins
    dynamically."""

    _plugin_dir = ''

    @classmethod
    def set_plugin_dir(cls, dir: str) -> None:
        # TODO check if dir exists
        cls._plugin_dir = dir

    @classmethod
    def find_plugins(cls, group: str= '') -> List[str]:
        """Finds plugins in the plugin directory, or from setuptools entrypoints

        This function is supposed to be called in settings.py after the
        INSTALLED_APPS variable. Therefore it can not use global variables from
        settings, to prevent circle imports.

        :param group: A string with the (dotted) group name, which the site
            packages are searched for. Matching plugins are found and added to
            the INSTALLED_APPS list, e.g. "myproject.plugins".
        :returns: A list of dotted app_names, which can be appended to
            INSTALLED_MODULES.
        """

        found_apps = []

        if group:
            for entry_point in iter_entry_points(group=group, name=None):
                found_apps.append(entry_point.module_name)

        # if there is no plugin_dir set, just ignore it and return yet found
        # plugins from pkg_resources entrypoints
        if not os.path.isdir(cls._plugin_dir):
            # this is an invalid directory
            return found_apps

        return found_apps

    @staticmethod
    def load_plugin_submodule(submodule: str) -> list:
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
        for appconfig in apps.get_app_configs():

            # import all the sumbodules from all plugin apps
            if hasattr(appconfig, 'PluginMeta'):
                try:
                    dotted_name = "%s.%s" % (appconfig.name, submodule)
                    module = importlib.import_module(dotted_name)
                    logger.debug('Successfully loaded submodule {}'.format(
                        dotted_name))
                    modules.append(module)
                except ImportError as e:
                    # ignore non-existing <package_name>.py files
                    # in plugins
                    logger.error("Error loading submodule '{}':\n   {}".format(
                        dotted_name, e))
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
            logger.debug('Django apps: {}'.format(
                apps.app_configs
            ))
    @staticmethod
    def collect_urls() -> list:
        """Loads all plugins' urls.py and collects their urlpatterns.

        This is maybe not the best approach, but it allows plugins to
        have "global" URLs, and not only namespaced, and it is flexible

        :returns: a list of urlpatterns that can be merged with the global
        urls.urlpattern.
        """

        # FIXME: the order the plugins are loaded is not deterministic. This can lead to serious problems,
        # as apps could use the same URL namespace, and depending on which one was loaded first, it may mask the other
        # URL. This has to be fixed. See [Issue #22](https://gitlab.com/nerdocs/medux/MedUX/issues/22)
        # Another unmanaged problem is 'dependencies' - a dependency manager must be implemented into the PluginManager
        urlpatterns = []
        for module in PluginManager.load_plugin_submodule('urls'):
            pattern = getattr(module, 'urlpatterns', None)
            if pattern:
                urlpatterns.append(pattern)

        return urlpatterns



