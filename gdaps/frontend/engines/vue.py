import shutil
import subprocess

from django.core.management import CommandError

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
