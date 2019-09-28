import os
import shutil
import subprocess
from typing import List

from django.conf import settings

from gdaps import implements, PluginError
from gdaps.frontend.api import IFrontendEngine
from gdaps.frontend import frontend_settings


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
        "src/plugins.js",
        "src/assets/logo.png",
        "src/components/HelloWorld.vue",
    ]

    @staticmethod
    def initialize(frontend_path):
        try:
            # yarn install vue
            # FIXME: check if yarn is available
            subprocess.check_call(
                "yarn install --cwd {}".format(frontend_path), shell=True
            )
        except Exception as e:
            shutil.rmtree(frontend_path)
            raise e

    @staticmethod
    def update_plugins_list(plugins_list: List[str]) -> None:
        """Writes plugins into plugins.js file, to be collected dynamically by webpack."""

        global_frontend_path = os.path.join(
            settings.BASE_DIR, frontend_settings.FRONTEND_DIR
        )
        if not os.path.exists(global_frontend_path):
            try:
                os.makedirs(global_frontend_path)
            except:
                raise PluginError(
                    f"Could not create frontend directory '{global_frontend_path}'."
                )
        try:
            plugins_file = open(os.path.join(global_frontend_path, "plugins.js"), "w")

            plugins_file.write("module.exports = [\n")

            counter = 1
            total = len(plugins_list)
            for app_name in plugins_list:
                plugins_file.write('  "' + os.path.join(app_name, "frontend") + '"')
                if counter < total:
                    plugins_file.write(",")
                plugins_file.write("\n")
                counter += 1

            plugins_file.write("]\n")
        except Exception as e:
            raise PluginError(
                str(e)
                + "\n "
                + f"Could not open plugins.js for writing. Please check write permissions in {global_frontend_path}."
            )
        finally:
            plugins_file.close()
