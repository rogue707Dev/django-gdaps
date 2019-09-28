import shutil
import subprocess

from gdaps import implements
from gdaps.frontend.api import IFrontendEngine


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

    def initialize(self, frontend_path):

        try:
            # yarn install vue
            # FIXME: check if yarn is available
            subprocess.check_call(
                "yarn install --cwd {}".format(frontend_path), shell=True
            )
        except Exception as e:
            shutil.rmtree(frontend_path)
            raise e
