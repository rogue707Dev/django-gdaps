import os
import logging
import shutil
import subprocess

import django
from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.apps import apps
from django.template import Context
from django.utils.version import get_docs_version

from gdaps import ExtensionPoint
from gdaps.frontend.api import IFrontendEngine
from gdaps.conf import gdaps_settings
from gdaps.frontend import current_engine
from gdaps.frontend.api import IFrontendEngines

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    help = "Initializes a Django GDAPS application with a Javascript frontend."
    rewrite_template_suffixes = (
        # Allow shipping invalid .py files without byte-compilation.
        (".py-tpl", ".py"),
    )

    # TODO: allow dynamic engines
    _engines = ExtensionPoint(IFrontendEngines)

    def is_supported_engine(self, engine):
        engine_names = [engine.name for engine in self._engines]
        if engine not in engine_names:
            raise CommandError(
                f"'{engine.name}' is not supported as frontend engine. Available engines are: {engine_names} "
            )

    def handle(self, **options):
        try:
            frontend_dir = settings.GDAPS["FRONTEND_DIR"]
        except:
            frontend_dir = "frontend"

        self.verbosity = options["verbosity"]

        if len(self._engines) == 0:
            raise CommandError("There is no frontend engine available.")

        # create a frontend/ directory in the Django root
        frontend_path = os.path.abspath(
            os.path.expanduser(os.path.join(settings.BASE_DIR, options["frontend_dir"]))
        )

        options["files"] += current_engine().files

        try:
            os.mkdir(frontend_path)
        except FileExistsError:
            raise CommandError(
                "There already seems to be a frontend directory with that name. "
                f"Please delete the '{frontend_dir}' directory if you want to create a new one."
            )

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
        extensions = ["js"]

        context = Context(
            {
                **options,
                "project_name": project_name,
                "project_title": project_title,
                "frontend_dir": frontend_dir,
                "frontend_path": frontend_path,
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

            for dirname in dirs[:]:
                if dirname.startswith(".") or dirname == "__pycache__":
                    dirs.remove(dirname)

            for filename in files:
                # FIXME: use Js specific file endings here
                if filename.endswith((".pyo", ".pyc", ".py.class")):
                    # Ignore some files as they cause various breakages.
                    continue
                old_path = os.path.join(root, filename)

                new_path = os.path.join(frontend_path, filename)
                for old_suffix, new_suffix in self.rewrite_template_suffixes:
                    if new_path.endswith(old_suffix):
                        new_path = new_path[: -len(old_suffix)] + new_suffix
                        break  # Only rewrite once

                if os.path.exists(new_path):
                    raise CommandError(
                        f"{new_path} already exists, overlaying a "
                        "frontend file into an existing directory won't replace conflicting files"
                    )

                # Only render intended files, as we don't want to
                # accidentally render Django templates files
                if new_path.endswith(extensions) or filename in extra_files:
                    with open(old_path, encoding="utf-8") as template_file:
                        content = template_file.read()
                    template = django.template.Engine().from_string(content)
                    content = template.render(context)
                    with open(new_path, "w", encoding="utf-8") as new_file:
                        new_file.write(content)
                else:
                    shutil.copyfile(old_path, new_path)

                if self.verbosity >= 2:
                    self.stdout.write(f"Creating {new_path}\n")
                try:
                    shutil.copymode(old_path, new_path)
                    self.make_writeable(new_path)
                except OSError:
                    self.stderr.write(
                        f"Notice: Couldn't set permission bits on {new_path}. You're "
                        "probably using an uncommon filesystem setup. No problem."
                    )

        self.engine.initialize(frontend_path)

        # build
        # subprocess.check_call(
        #     "npm run build --prefix {base_dir}/{plugin}/frontend".format(
        #         plugin=target, base_dir=settings.BASE_DIR
        #     ),
        #     shell=True,
        # )

        # ask the user to be sure to copy the static files
        # subprocess.check_call('./manage.py collectstatic'.format(plugin=target, base_dir=settings.BASE_DIR), shell=True)

    def make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)
