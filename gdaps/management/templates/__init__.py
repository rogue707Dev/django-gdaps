import logging
import os
import shutil
import stat
from os import path

import django
from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.template import Context
from django.utils.version import get_docs_version

logger = logging.getLogger(__file__)


class TemplateCommand(BaseCommand):
    help = "Copies a template to a given directory using Django template replacements"

    # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's _name.
    # If there is a better way to do that - please let me know.
    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    # Directories that are searched for template files
    templates = []

    # Path where to copy to
    target_path = None

    # Extensions of files which are rendered, not copied
    extensions = ()

    # extra files which are rendered too instead of copied
    extra_files = []

    # Files/directories that are generally excluded from copying
    excluded = ["__pycache__"]

    # A dict of options. Use self.context.update({...}) to append another dict to it
    context = {"docs_version": get_docs_version(), "django_version": django.__version__}

    # A tuple of 2-tuples for rewriting file suffixes
    rewrite_template_suffixes = ()

    # deprecated
    verbosity = 0

    def create_directory(self, path):
        try:
            os.makedirs(path)
        except FileExistsError:
            raise CommandError(
                "There already seems to be a directory with that name. "
                f"Please delete the '{path}' directory before you expand a template there."
            )

    def _render_path(self, path: str) -> str:
        """Replaces context variables in path."""
        if not "{" in path:
            return path
        for var, replacement in self.context.items():
            path = path.replace("{" + var + "}", str(replacement))
        return path

    def copy_templates(self):
        assert self.target_path is not None
        assert self.templates is not None
        assert self.rewrite_template_suffixes is not None

        # Setup a stub settings environment for template rendering
        if not settings.configured:
            settings.configure()
            django.setup()

        top_dir = os.path.abspath(path.expanduser(self.target_path))

        for template_dir in self.templates:
            prefix_length = len(template_dir) + 1

            for root, dirs, files in os.walk(template_dir):

                path_rest = root[prefix_length:]
                relative_dir = self._render_path(path_rest)
                if relative_dir:
                    target_dir = path.join(top_dir, relative_dir)
                    if not path.exists(target_dir):
                        os.mkdir(target_dir)

                for dirname in dirs[:]:
                    if dirname.startswith(".") or dirname in self.excluded:
                        dirs.remove(dirname)

                for filename in files:
                    old_path = os.path.join(root, filename)

                    new_path = os.path.join(
                        top_dir,
                        self._render_path(path_rest),
                        self._render_path(filename),
                    )
                    for (old_suffix, new_suffix) in self.rewrite_template_suffixes:
                        if new_path.endswith(old_suffix):
                            new_path = new_path[: -len(old_suffix)] + new_suffix
                            break  # Only rewrite once

                    if os.path.exists(new_path):
                        logger.error(
                            f"{new_path} already exists, overlaying a "
                            f"template file {old_path} into an existing directory won't replace conflicting files"
                        )

                    if self.verbosity >= 2:
                        logger.info(f"Creating {new_path}.\n")

                    # Only render intended files, as we don't want to
                    # accidentally render Django templates files
                    if (
                        new_path.endswith(
                            tuple([pair[1] for pair in self.rewrite_template_suffixes])
                        )
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
                        logger.error(
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
