import logging
import os
import shutil
import subprocess
from typing import List

from django.conf import settings
from django.core.management import CommandError

from gdaps import implements
from gdaps.exceptions import PluginError
from gdaps.api import IGdapsPlugin
from gdaps.frontend import frontend_settings
from gdaps.frontend.api import IFrontendEngine

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


@implements(IFrontendEngine)
class VueEngine:
    name = "vue"
    extensions = ("js",)
    rewrite_template_suffixes = ((".js-tpl", ".js"),)
    extra_files = []
    __package_manager = None

    @classmethod
    def initialize(cls, frontend_dir, package_manager):
        """Initializes an already created frontend using 'npm/yarn install'."""

        cls.__package_manager = package_manager
        # this method can assume that the frontend_path exists
        frontend_path = None
        try:
            frontend_path = os.path.join(settings.BASE_DIR, frontend_dir)
            # yarn install vue
            if shutil.which(package_manager["name"]) is None:
                raise CommandError(
                    f"'{package_manager['name']}' command is not available. Aborting."
                )

            if shutil.which("vue") is None:
                subprocess.check_call(
                    package_manager["installglobal"].format(
                        pkg="@vue/cli @vue/cli-service-global"
                    ),
                    shell=True,
                )

            subprocess.check_call(
                f"vue create --packageManager {package_manager['name']} --no-git --force {frontend_dir}",
                cwd=settings.BASE_DIR,
                shell=True,
            )

            subprocess.check_call(
                package_manager["install"].format(pkg="webpack-bundle-tracker"),
                cwd=frontend_path,
                shell=True,
            )
        except Exception as e:
            # FIXME: frontend_path/ was not created here - shouldn't be destroyed here!
            if frontend_path:
                shutil.rmtree(frontend_path)
            raise e

    @staticmethod
    def update_plugins_list(plugin_names: List[str]) -> None:
        """Writes plugins into plugins.js file, to be collected dynamically by webpack."""

        if not os.path.exists(frontend_settings.FRONTEND_DIR):
            logger.warning(
                f"Could not find frontend directory '{frontend_settings.FRONTEND_DIR}'."
            )
            return

        with open(
            os.path.join(frontend_settings.FRONTEND_DIR, "plugins.js"), "w"
        ) as plugins_file:

            plugins_file.write("module.exports = [\n")

            counter = 1
            total = len(plugin_names)
            for app_name in plugin_names:
                plugin_frontend_entry_point = os.path.join(app_name, "frontend")
                if os.path.exists(
                    os.path.join(plugin_frontend_entry_point, "index.js")
                ):
                    logger.info(f"Found entry point in GDAPS plugin {app_name}.")
                    plugins_file.write(f'  "{plugin_frontend_entry_point}"')
                    if counter < total:
                        plugins_file.write(",")
                    plugins_file.write("\n")
                    counter += 1
                else:
                    logger.info(f"No entry point found in {app_name}. Skipping")

            plugins_file.write("]\n")


@implements(IGdapsPlugin)
class VuePlugin:
    def plugin_synchronized(self, app):
        if not os.path.exists(os.path.join(app.path, "frontend", "index.js")):
            logger.info(f"    - {app.name} - no frontend found.")
        else:
            logger.info((f"    - {app.name} - frontend found."))
