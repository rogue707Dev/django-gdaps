import os
import shutil

from django.conf import settings
from django.core.management import CommandError
from nltk import PorterStemmer

from gdaps.frontend import IFrontendEngine
from gdaps.frontend.pkgmgr import PipenvPackageManager, current_package_manager
from gdaps.pluginmanager import PluginManager


class PySideEngine(IFrontendEngine):
    name = "pyside"
    extensions = ("js",)
    rewrite_template_suffixes = ((".py-tpl", ".py"), )
    extra_files = []
    __stemmed_group = None
    package_managers = [PipenvPackageManager]

    @classmethod
    def _singular_plugin_name(cls, plugin):
        if not cls.__stemmed_group:
            cls.__stemmed_group = PorterStemmer().stem(
                PluginManager.group.replace(".", "_")
            )
        return f"{cls.__stemmed_group}_{plugin.label}"

    @classmethod
    def initialize(cls, frontend_dir: str):
        """Initializes an already created frontend using 'pip install'."""

        cls.__package_manager = current_package_manager()

        if shutil.which(cls.__package_manager.name) is None:
            raise CommandError(
                f"'{cls.__package_manager.name}' command is not available. Aborting."
            )

        # this method can assume that the frontend_path exists
        frontend_path = os.path.join(settings.BASE_DIR, frontend_dir)

        cls.__package_manager.install("pyside2", cwd=frontend_path)

    @classmethod
    def update_plugins_list(cls) -> None:
        """Updates the list of installed PySide frontend plugins.

        This implementation makes sure that all paths are installed by the package manager."""

        # first get a list of plugins which have a frontend part.
        plugins_with_frontends = []
        for plugin in PluginManager.plugins():
            if plugin.name in ["gdaps", "gdaps.frontend"]:
                continue
            else:
                if os.path.exists(
                        os.path.join(plugin.path, "frontend-pyside", "package.json")
                ):
                    plugins_with_frontends.append(plugin)

