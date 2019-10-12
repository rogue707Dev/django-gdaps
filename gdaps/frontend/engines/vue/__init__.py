import json
import logging
import os
import shutil
import subprocess

from django.conf import settings
from django.core.management import CommandError

from gdaps.api import IGdapsPlugin
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
    rewrite_template_suffixes = ((".js-tpl", ".js"),)
    extra_files = []
    __package_manager = None

    @classmethod
    def initialize(cls, frontend_dir: str, package_manager: IPackageManager):
        """Initializes an already created frontend using 'npm/yarn install'."""

        cls.__package_manager = package_manager
        # this method can assume that the frontend_path exists
        frontend_path = None
        try:
            frontend_path = os.path.join(settings.BASE_DIR, frontend_dir)
            # yarn install vue
            if shutil.which(package_manager.name) is None:
                raise CommandError(
                    f"'{package_manager.name}' command is not available. Aborting."
                )

            if shutil.which("vue") is None:
                subprocess.check_call(
                    package_manager.installglobal.format(
                        pkg="@vue/cli @vue/cli-service-global"
                    ),
                    shell=True,
                )

            subprocess.check_call(
                f"vue create --packageManager {package_manager.name} --no-git --force {frontend_dir}",
                cwd=settings.BASE_DIR,
                shell=True,
            )

            subprocess.check_call(
                package_manager.install.format(pkg="webpack-bundle-tracker"),
                cwd=frontend_path,
                shell=True,
            )
        except Exception as e:
            # FIXME: frontend_path/ was not created here - shouldn't be destroyed here!
            if frontend_path:
                shutil.rmtree(frontend_path)
            raise e

    @staticmethod
    def update_plugins_list() -> None:
        """Updates the list of installed frontend plugins.

        This implementation makes sure that all paths are installed by the package manager,
        to be collected dynamically by webpack.
        """

        # first get a list of plugins which have a frontend part.
        # we ignore gdaps itself and then check for a "frontend" directory int the plugin's dir.
        plugins_with_frontends = PluginManager.plugins()
        for plugin in plugins_with_frontends:
            if plugin.label == "gdaps":
                plugins_with_frontends.remove(plugin)
                continue
            if not os.path.exists(os.path.join(plugin.path, "frontend")):
                plugins_with_frontends.remove(plugin)

        global_frontend_path = os.path.join(
            settings.BASE_DIR, frontend_settings.FRONTEND_DIR
        )
        with open(
            os.path.join(
                settings.BASE_DIR, frontend_settings.FRONTEND_DIR, "package.json"
            ),
            "r",
            encoding="utf-8",
        ) as packages_file:
            try:
                dependencies = json.load(packages_file)["dependencies"]
                for plugin in plugins_with_frontends:
                    frontend_dir = (
                        f"{PluginManager.group.replace('.','-')}-{plugin.label}"
                    )
                    plugin.path = os.path.join(plugin.path, "frontend", frontend_dir)

                    if not frontend_dir in dependencies:
                        # install missing dependencies
                        subprocess.check_call(
                            current_package_manager().install.format(pkg=frontend_dir),
                            cwd=global_frontend_path,
                        )
            except:
                raise CommandError("Error parsing package.json.")

        if not os.path.exists(global_frontend_path):
            logger.warning(
                f"Could not find frontend directory '{global_frontend_path}'."
            )
            return

        # with open(
        #     os.path.join(global_frontend_path, "plugins.js"), "w"
        # ) as plugins_file:
        #
        #     plugins_file.write("module.exports = [\n")
        #
        #     counter = 1
        #     total = len(plugin_paths)
        #     for app_name in plugin_paths:
        #         plugin_frontend_entry_point = os.path.join(app_name, "frontend")
        #         if os.path.exists(
        #             os.path.join(plugin_frontend_entry_point, "index.js")
        #         ):
        #             logger.info(f"Found entry point in GDAPS plugin {app_name}.")
        #             plugins_file.write(f'  "{plugin_frontend_entry_point}"')
        #             if counter < total:
        #                 plugins_file.write(",")
        #             plugins_file.write("\n")
        #             counter += 1
        #         else:
        #             logger.info(f"No entry point found in {app_name}. Skipping")
        #
        #     plugins_file.write("]\n")


class VuePlugin(IGdapsPlugin):
    def plugin_synchronized(self, app):
        if not os.path.exists(os.path.join(app.path, "frontend", "index.js")):
            logger.info(f"    - {app.name} - no frontend found.")
        else:
            logger.info((f"    - {app.name} - frontend found."))
