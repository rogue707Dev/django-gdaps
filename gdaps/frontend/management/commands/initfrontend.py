import os
import logging
import shutil
import subprocess

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
        parser.add_argument(
            "--frontend_dir",  # FIXME: rename to --frontend-dir
            type=str,
            default="frontend",
            help="Specify custom frontend directory within project",
        )

    def handle(self, *args, **options):

        # check if the engine is supported
        # TODO: allow dynamic engines
        if options["engine"] not in _engines:
            raise CommandError(
                "'{}' is not supported as frontend engine. Available engines are: {} ".format(
                    options["engine"], _engines
                )
            )

        # preparation
        options["project_name"] = self._django_root
        options["project_title"] = self._django_root.title().replace("_", " ")
        options["files"] = []
        options["extensions"] = []

        # create a frontend/ directory in the Django root
        frontend_path = os.path.join(settings.BASE_DIR, options["frontend_dir"])

        if os.path.exists(frontend_path):
            raise CommandError(
                "There already seems to be a frontend with that name in project '{project}'. "
                "Please delete the '{frontend}' directory if you want to create a new one, "
                "or choose another name using --frontend_dir.".format(
                    project=options["project_name"], frontend=options["frontend_dir"]
                )
            )

        os.mkdir(frontend_path)

        # extend a plugin with vuejs
        if options["engine"] == "vue":

            if not os.path.exists(frontend_path):
                os.mkdir(frontend_path)

            # create files
            template = os.path.join(
                apps.get_app_config("frontend").path,
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
                    "A 'frontend/' directory was created in {}. ".format(
                        settings.BASE_DIR
                    )
                )
                # npm install vue
                # FIXME: check if npm is available
                subprocess.check_call(
                    "yarn install --cwd {}".format(frontend_path), shell=True
                )

            except Exception as e:
                shutil.rmtree(frontend_path)
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
