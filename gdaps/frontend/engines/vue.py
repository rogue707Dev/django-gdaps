import logging
import os
import shutil
import subprocess
from typing import List


from gdaps import implements
from gdaps.exceptions import PluginError
from gdaps.api import IGdapsPlugin
from gdaps.frontend import frontend_settings
from django.core.management import CommandError
from gdaps.frontend.api import IFrontendEngine

logger = logging.getLogger(__file__)

# TODO: use header text replacing instead of manually writing a file.
header = """
// plugins.js
//
// This is a special file that is created by GDAPS automatically
// using the 'startplugin' and 'syncplugins' management command.
// Only touch this file if you exactly know what you are doing.
// it will be overwritten with every run of 'manage.py startplugin/syncplugin'

module.exports = {plugins}
"""


@implements(IFrontendEngine)
class VueEngine:
    name = "vue"
    files = [
        ".gitignore",
        "babel.config.js",
        "package.json",  # contains dependencies
        "vue.config.js",
        "src/App.vue",
        "src/main.js",
        "src/assets/logo.png",
        "src/components/HelloWorld.vue",
    ]

    @staticmethod
    def initialize(frontend_path):
        """Initializes an already created frontend using 'yarn install'."""
        try:
            # yarn install vue
            if shutil.which("yarn") is None:
                raise CommandError("Yarn is not available. Please install yarn.")
            subprocess.check_call(f"yarn install --cwd {frontend_path}", shell=True)
        except Exception as e:
            shutil.rmtree(frontend_path)
            raise e

    @staticmethod
    def update_plugins_list(plugins_list: List[str]) -> None:
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
            total = len(plugins_list)
            for app_name in plugins_list:
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
