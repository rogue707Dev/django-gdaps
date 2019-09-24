import os
import shutil
import subprocess

from django.core.management import CommandError

from gdaps import implements
from gdaps.conf import gdaps_settings
from gdaps.frontend.api import IFrontendEngine
from gdaps.pluginmanager import PluginManager

header = """
// plugins.js
//
// This is a special file that is created by GDAPS automatically
// using the 'startplugin' and 'syncplugins' management command.
// Only touch this file if you exactly know what you are doing.
// it will be overwritten with every run of 'manage.py startplugin <xyz>'

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
    def syncplugins(frontend_path):
        plugin_list = []
        for app in PluginManager.plugins(skip_disabled=True):
            try:
                plugin_frontend_entrypoint = os.path.join(
                    app.module.__file__,
                    gdaps_settings.GDAPS["FRONTEND_DIR"],
                    "index.js",
                )
                if os.path.exists(plugin_frontend_entrypoint):
                    plugin_list.append(plugin_frontend_entrypoint)
            except FileNotFoundError:
                pass

        with open(os.path.join(frontend_path, "plugins.js"), "w") as pluginsfile:
            pluginsfile.write(header.replace("{plugins}", str(plugin_list)))
