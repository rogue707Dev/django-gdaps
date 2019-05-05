import os
import string
import logging

from django.conf import settings
from gdaps.conf import gdaps_settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
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
    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    # absolute path to internal plugins of application
    plugin_path = os.path.join("BASE_DIR", *gdaps_settings.PLUGIN_PATH.split("."))

    help = (
        "Creates a basic GDAPS plugin structure in the "
        "'{}/' directory from a template.".format(plugin_path)
    )

    missing_args_message = "You must provide a plugin _name."

    def handle(self, name, **options):
        from django.core.validators import validate_email

        plugin_path = PluginManager.plugin_path

        logger.debug("Using plugin directory: {}".format(plugin_path))

        # override target directory
        target = os.path.join(*plugin_path.split("."), name)

        if os.path.exists(target):
            raise CommandError("'{}' already exists".format(target))

        # override plugin template directory
        del options["template"]
        template = os.path.join(
            apps.get_app_config("gdaps").path, "management", "templates", "plugin"
        )
        options["files"] += ["README.md"]

        options["upper_cased_app_name"] = name.upper()

        # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's _name.
        # If there is a better way to do that - please let me know.
        options["project_name"] = self._django_root
        options["plugin_path"] = plugin_path
        options["project_title"] = self._django_root.capitalize()

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

        try:
            os.makedirs(target)
            self.stdout.write(
                "Successfully created plugin directory: {}\n".format(target)
            )
        except OSError as e:
            raise CommandError(e)

        super().handle("app", name, target, template=template, **options)

        self.stdout.write(
            "Please adapt '%s' to your needs.\n"
            % os.path.join(settings.BASE_DIR, target, "setup.py")
        )
