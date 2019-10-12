import os
import string
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError

from gdaps.management.templates import TemplateCommand
from django.apps import apps

from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__name__)

try:
    # if git is available, make use of git username/email config data
    import git

    reader = git.Repo.init(settings.BASE_DIR).config_reader()
except:
    reader = None


def _snake_case_to_spaces(name):
    return string.capwords(name, "_").replace("_", " ")


def get_user_data(key):
    if reader:
        return reader.get_value("user", key, default="")
    else:
        return ""


class Command(TemplateCommand):
    """This is the managemant command to add a plugin from a template to a Django application."""

    # absolute path to internal plugins of application
    plugin_path = os.path.join(settings.BASE_DIR, *PluginManager.group.split("."))

    help = (
        "Creates a basic GDAPS plugin structure in the "
        f"'{plugin_path}/' directory from a template."
    )
    missing_args_message = "You must provide a plugin name."

    def add_arguments(self, parser):
        parser.add_argument("name")

    def handle(self, name, **options):

        from django.core.validators import validate_email

        plugin_path = PluginManager.plugin_path()
        logger.debug("Using plugin directory: {}".format(self.plugin_path))

        self.rewrite_template_suffixes += (
            ("py-tpl", "py"),
            ("md-tpl", "md"),
            ("in-tpl", "in"),
            ("cfg-tpl", "cfg"),
            ("rst-tpl", "rst"),
        )

        # override target directory
        self.target_path = os.path.join(*self.plugin_path.split("."), name)

        if os.path.exists(self.target_path):
            raise CommandError("'{}' already exists".format(self.target_path))

        # override plugin template directory
        self.templates.append(
            os.path.join(
                apps.get_app_config("gdaps").path, "management", "templates", "plugin"
            )
        )

        parameters = [
            # key, value, default, validator/None
            ("author", "Author", get_user_data("name"), None),
            ("author_email", "Email", get_user_data("email"), validate_email),
        ]
        for key, prompt, default, validator in parameters:
            s = ""
            while not s:
                format_str = "{} [{}]: " if default else "{}: "
                s = input(format_str.format(prompt, default))
                # don't let input string contain a "
                if '"' in s:
                    self.stderr.write(
                        "Error: The character '\"' is not allowed within the string.\n"
                    )
                if default and not s:
                    s = default
                if validator:
                    try:
                        validator(s)
                    except ValidationError as e:
                        self.stderr.write(e.message + "\n")
                        s = ""

            options[key] = s
        camel_cased_name = "".join(x for x in name.title() if x != "_")
        self.context.update(
            {
                **options,
                "app_name": name,
                "camel_case_app_name": camel_cased_name,
                "upper_cased_app_name": name.upper(),
                "spaced_app_name": _snake_case_to_spaces(name),
                "project_name": self._django_root,
                "plugin_path": plugin_path,
                "project_title": self._django_root.capitalize(),
                "plugin_group": PluginManager.group,
            }
        )

        self.create_directory(self.target_path)

        self.copy_templates()

        logger.info(f"Successfully created plugin: {self.target_path}\n")
        logger.info(
            f"Add '{PluginManager.group}.{name}.{camel_cased_name}Config' to your INSTALLED_APPS or install it via pip/pipenv"
        )
        logger.info(
            f"Please adapt '{os.path.join(self.target_path, 'setup.cfg')}' to your needs.\n"
        )
