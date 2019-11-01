import json
import logging
import os
import shutil
import subprocess
from typing import Dict

from django.conf import settings
from django.core.management import CommandError
from nltk import PorterStemmer

from gdaps.apps import GdapsConfig
from gdaps.frontend.api import IFrontendEngine, IPackageManager
from gdaps.frontend.conf import frontend_settings
from gdaps.frontend.pkgmgr import current_package_manager
from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__file__)

# TODO: use header text replacing instead of manually writing a file.
header = """
// plugins.js
//
// This is a special file that is created by GDAPS automatically
// using the 'startplugin' and 'syncplugins' management command.
// Only touch this file if you exactly know what you are doing.
// It will be overwritten with every run of 'manage.py startplugin/syncplugin'

module.exports = {plugins}
"""


class VueEngine(IFrontendEngine):
    name = "vue"
    extensions = ("js",)
    rewrite_template_suffixes = ((".js-tpl", ".js"), (".json-tpl", ".json"))
    extra_files = []
    __package_manager = None

    @classmethod
    def initialize(cls, frontend_dir: str, package_manager: IPackageManager):
        """Initializes an already created frontend using 'npm/yarn install'.
        """

        cls.__package_manager = package_manager

        if shutil.which(package_manager.name) is None:
            raise CommandError(
                f"'{package_manager.name}' command is not available. Aborting."
            )
        if shutil.which("vue") is None:
            package_manager.installglobal(
                "@vue/cli @vue/cli-service-global", cwd=settings.BASE_DIR
            ),

        # this method can assume that the frontend_path exists
        frontend_path = None
        frontend_path = os.path.join(settings.BASE_DIR, frontend_dir)
        # yarn install vue

        subprocess.check_call(
            f"vue create --packageManager {package_manager.name} --no-git --force {frontend_dir}",
            cwd=settings.BASE_DIR,
            shell=True,
        )

        package_manager.install("webpack-bundle-tracker", cwd=frontend_path)

    @staticmethod
    def update_plugins_list() -> None:
        """Updates the list of installed Vue frontend plugins.

        This implementation makes sure that all paths are installed by the package manager,
        to be collected dynamically by webpack.
        """

        # first get a list of plugins which have a frontend part.
        # we ignore gdaps itself and then check for a "frontend" directory int the plugin's dir.
        plugins_with_frontends = []
        for plugin in PluginManager.plugins():
            if plugin.label in ["gdaps", "frontend"]:
                continue
            else:
                if os.path.exists(os.path.join(plugin.path, "frontend")):
                    plugins_with_frontends.append(plugin)

        global_frontend_path = os.path.join(
            settings.BASE_DIR, frontend_settings.FRONTEND_DIR
        )
        global_package_file = os.path.join(
            settings.BASE_DIR, frontend_settings.FRONTEND_DIR, "package.json"
        )
        with open(global_package_file, "r", encoding="utf-8") as f:
            try:
                global_package_data = json.load(f)
                dependencies = global_package_data["dependencies"]  # type:Dict[str,str]
            except:
                raise CommandError("Error parsing global package.json.")

            # check if plugin frontend is listed in package.json dependencies.
            # If not, install this plugin frontend package
            for plugin in plugins_with_frontends:
                frontend_package_name = f"{PorterStemmer().stem(PluginManager.group.replace('.','-'))}-{plugin.label}"

                plugin_path = os.path.join(
                    plugin.path, "frontend", frontend_package_name
                )

                # replace/update js package version with gdaps plugin version
                with open(
                    os.path.join(plugin_path, "package.json"), "r+"
                ) as plugin_package_file:
                    data = json.load(plugin_package_file)
                    data["version"] = plugin.PluginMeta.version

                    # set plugins as private. They should keep with the Django part, and never be uploaded into a repo.
                    data["private"] = True

                    plugin_package_file.seek(0)
                    json.dump(data, plugin_package_file, indent=2)
                    plugin_package_file.truncate()

                # if installed plugin with frontend support is not listed in global package.json,
                # install it with package manager
                if not frontend_package_name in dependencies:
                    # install missing dependencies
                    current_package_manager().install(
                        plugin_path, cwd=global_frontend_path
                    )

            # if global package.json lists an orphaned Js package
            # which is not installed on the python side any more,
            # uninstall that package. If that fails, remove the line?
            for dep in dependencies:
                if not dep.startswith(f"{PluginManager.group.replace('.','-')}"):
                    # ignore foreign dependency packages like webpack-bundle-tracker etc.
                    continue

                if not dep in [
                    f"{PluginManager.group.replace('.','-')}-{plugin.label}"
                    for plugin in plugins_with_frontends
                ]:
                    # dependency has no corresponding installed plugin any more. Uninstall.
                    logger.info(f" ✘ Uninstalling '{dep}'")
                    current_package_manager().uninstall(dep, cwd=global_frontend_path)

        if not os.path.exists(global_frontend_path):
            logger.warning(
                f"Could not find frontend directory '{global_frontend_path}'."
            )
            return
