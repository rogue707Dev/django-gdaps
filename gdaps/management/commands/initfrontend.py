import os
import string
import logging
import sys
import importlib.util
import subprocess
import shutil

from .startplugin import get_user_data

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.core.management.templates import TemplateCommand
from django.apps import apps
from gdaps.conf import gdaps_settings

logger = logging.getLogger(__name__)

_engines = ["vue"]


class Command(TemplateCommand):

    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    help = "Initializes a Django GDAPS application with an Javascript frontend (currently only Vue.js supported)."

    def add_arguments(self, parser):
        parser.add_argument(
            "engine",
            type=str,
            help="Specify Javascript framework that should be added to a GDAPS application.\n"
            "Available engines are: {}.".format(", ".join(_engines)),
        )

    def handle(self, *args, **options):

        # check if the engine is supported
        # TODO: allow dynamic engines
        if options["engine"] not in _engines:
            raise CommandError(
                "'{}' is not supported as frontend engine.".format(options["engine"])
            )

        # preparation
        options["project_name"] = self._django_root
        options["project_title"] = self._django_root.title().replace("_", " ")
        options["files"] = []
        options["extensions"] = []

        # create a frontend/ directory in the drupal root
        frontend_path = os.path.join(gdaps_settings.FRONTEND_PATH)

        if os.path.exists(frontend_path):
            raise CommandError(
                "There already seems to be a frontend in project '{}'. "
                "Please delete the 'frontend' directory if you want to create a new one.".format(
                    options["project_name"]
                )
            )

        os.mkdir(frontend_path)

        # extend a plugin with vuejs
        if options["engine"] == "vue":

            if not os.path.exists(frontend_path):
                os.mkdir(frontend_path)

            # create files
            template = os.path.join(
                apps.get_app_config("gdaps").path,
                "management",
                "templates",
                "frontend",
                "vue",
            )
            options["files"] += [
                ".gitignore",
                "babel.config.js",
                "package.json",  # contains dependencies
                "vue.config.js",
                "src/App.vue",
                "src/main.js",
                "src/assets/logo.png",
                "src/components/HelloWorld.vue",
            ]

            try:
                super().handle(
                    "app",
                    options["project_name"] + "_frontend",
                    target=frontend_path,
                    template=template,
                    **options,
                )

                print(
                    "A 'frontend/' directory was created in {}. "
                    "Please run 'npm install' in that directory to install the Vue components".format(
                        settings.BASE_DIR
                    )
                )
                # npm install vue
                # FIXME: check if npm is available
                # subprocess.check_call(
                #     "npm install --prefix {frontend_path}".format(
                #         frontend_path=frontend_path
                #     ),
                #     shell=True,
                # )

            except Exception as e:
                os.rmdir(frontend_path)
                raise e

            # build
            # subprocess.check_call(
            #     "npm run build --prefix {base_dir}/{plugin}/frontend".format(
            #         plugin=target, base_dir=settings.BASE_DIR
            #     ),
            #     shell=True,
            # )

            # ask the user to be sure to copy the static files
            # subprocess.check_call('./manage.py collectstatic'.format(plugin=target, base_dir=settings.BASE_DIR), shell=True)