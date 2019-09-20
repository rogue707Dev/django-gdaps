import os
import logging
import shutil
import subprocess
import sys

import django
from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.apps import apps
from django.template import Context
from django.utils.version import get_docs_version

from gdaps.conf import gdaps_settings

logger = logging.getLogger(__name__)

# TODO: allow dynamic engines
_engines = ["vue"]


class Command(BaseCommand):

    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    help = "Initializes a Django GDAPS application with a Javascript frontend."
    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        (".py-tpl", ".py"),
    )

    def is_supported_engine(self, engine):
        if engine not in _engines:
            raise CommandError(
                f"'{engine}' is not supported as frontend engine. Available engines are: {_engines} "
            )

    def handle(self, **options):
        options["frontend_dir"] = settings.GDAPS["FRONTEND_DIR"]
        try:
            self.engine = settings.GDAPS["FRONTEND_ENGINE"]
        except:
            self.engine = "vue"

        # TODO: add verbosity flag
        self.verbosity = options["verbosity"]

        # TODO: allow dynamic (plugin?) engines
        if not self.engine in ["vue"]:
            raise CommandError(f"Engine [self.engine] not supported.")

        # create a frontend/ directory in the Django root
        frontend_path = os.path.join(settings.BASE_DIR, options["frontend_dir"])

        if os.path.exists(frontend_path):
            raise CommandError(
                "There already seems to be a frontend directory with that name. "
                f"Please delete the '{options['frontend_dir']}' directory if you want to create a new one, "
            )

        os.mkdir(frontend_path)

        extra_files = []
        for file in options["files"]:
            extra_files.extend(map(lambda x: x.strip(), file.split(",")))
        if self.verbosity >= 2:
            self.stdout.write(
                "Rendering frontend files with "
                f"filenames: {', '.join(extra_files)}\n"
            )

        project_name = self._django_root
        project_title = self._django_root.title().replace("_", " ")
        files = []
        extensions = []

        context = Context(
            {
                **options,
                "project_name": project_name,
                "project_title": project_title,
                "docs_version": get_docs_version(),
                "django_version": django.__version__,
            },
            autoescape=False,
        )

        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        template_dir = os.path.join(
            apps.get_app_config("frontend").path,
            "management",
            "templates",
            "frontend",
            self.engine,
        )
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):

            path_rest = root[prefix_length:]
            # FIXME
            relative_dir = path_rest.replace(base_name, name)
            if relative_dir:
                target_dir = os.path.join(frontend_path, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

            for dirname in dirs[:]:
                if dirname.startswith(".") or dirname == "__pycache__":
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith((".pyo", ".pyc", ".py.class")):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)
                new_path = os.path.join(
                    frontend_path, relative_dir, filename.replace(base_name, name)
                )
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[: -len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                # FIXME: maybe foo.py AND foo.py-tpl exist. Print arror! Don't overwrite!

                # Only render intended files, as we don't want to
                # accidentally render Django templates files
                if new_path.endswith(extensions) or filename in extra_files:
                    with open(old_path, encoding="utf-8") as template_file:
                        content = template_file.read()
                    template = Engine().from_string(content)
                    content = template.render(context)
                    with open(new_path, "w", encoding="utf-8") as new_file:
                        new_file.write(content)
                else:
                    shutil.copyfile(old_path, new_path)

                if self.verbosity >= 2:
                    self.stdout.write("Creating %s\n" % new_path)
                try:
                    shutil.copymode(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        "Notice: Couldn't set permission bits on %s. You're "
                        "probably using an uncommon filesystem setup. No "
                        "problem." % new_path,
                        self.style.NOTICE,
                    )

    def handle(self, *args, **options):

        # check if the engine is supported

        # preparation
        options["project_name"] = self._django_root
        options["project_title"] = self._django_root.title().replace("_", " ")
        options["files"] = []
        options["extensions"] = []

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
                "src/plugins.js",
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

                # yarn install vue
                # FIXME: check if yarn is available
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
