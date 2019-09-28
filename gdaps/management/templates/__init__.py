import os
import shutil
import stat
from os import path

import django
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.template import Context
from django.core.management.templates import TemplateCommand as TC
from django.utils.version import get_docs_version

from gdaps.frontend import current_engine


class TemplateCommand(BaseCommand):
    help = "Copies a template to a given directory using Django template replacements"

    # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's _name.
    # If there is a better way to do that - please let me know.
    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    templates = []
    target_path = None
    excluded = ["__pycache__"]  # Files excluded from copying
    extensions = ()  # TODO:  extensions that are copied. If empty, all are taken.

    # A dict of options. Use self.context.update({...}) to append another dict to it
    context = {"docs_version": get_docs_version(), "django_version": django.__version__}

    # A tuple of 2-tuples for rewriting file suffixes
    rewrite_template_suffixes = (
        ("py-tpl", "py"),
        ("md-tpl", "md"),
        ("in-tpl", "in"),
        ("cfg-tpl", "cfg"),
        ("js-tpl", "js"),
    )
    verbosity = 0

    # extra files which are rendered too instead of copied
    extra_files = []

    def create_directory(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            raise CommandError(
                "There already seems to be a directory with that name. "
                f"Please delete the '{path}' directory before you expand a template there."
            )

    def copy_templates(self):
        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        if self.target_path is None:
            raise CommandError("No target path defined.")

        top_dir = os.path.abspath(path.expanduser(self.target_path))

        for template_dir in self.templates:
            prefix_length = len(template_dir) + 1

            for root, dirs, files in os.walk(template_dir):

                path_rest = root[prefix_length:]
                if path_rest:
                    target_dir = path.join(top_dir, path_rest)
                    if not path.exists(target_dir):
                        os.mkdir(target_dir)

                for dirname in dirs[:]:
                    if dirname.startswith(".") or dirname in self.excluded:
                        dirs.remove(dirname)

                for filename in files:
                    # FIXME: use Js specific file endings here
                    # if filename.endswith((".pyo", ".pyc", ".py.class")):
                    #     # Ignore some files as they cause various breakages.
                    #     continue
                    old_path = os.path.join(root, filename)

                    new_path = os.path.join(top_dir, path_rest, filename)
                    for (old_suffix, new_suffix) in self.rewrite_template_suffixes:
                        if new_path.endswith(old_suffix):
                            new_path = new_path[: -len(old_suffix)] + new_suffix
                            break  # Only rewrite once

                    if os.path.exists(new_path):
                        self.stderr.write(
                            f"{new_path} already exists, overlaying a "
                            f"template file {old_path} into an existing directory won't replace conflicting files"
                        )

                    if self.verbosity >= 2:
                        self.stdout.write(f"Creating {new_path}.\n")

                    # Only render intended files, as we don't want to
                    # accidentally render Django templates files
                    if (
                        new_path.endswith(self.extensions)
                        or filename in self.extra_files
                    ):
                        with open(old_path, encoding="utf-8") as template_file:
                            content = template_file.read()
                        template = django.template.Engine().from_string(content)
                        content = template.render(
                            Context(self.context, autoescape=False)
                        )
                        with open(new_path, "w", encoding="utf-8") as new_file:
                            new_file.write(content)
                    else:
                        shutil.copyfile(old_path, new_path)

                    try:
                        shutil.copymode(old_path, new_path)
                        self.make_writeable(new_path)
                    except OSError:
                        self.stderr.write(
                            f"Notice: Couldn't set permission bits on {new_path}. You're "
                            "probably using an uncommon filesystem setup. No problem."
                        )

    def handle(self, *args, **options):
        self.verbosity = options["verbosity"]

    def make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)