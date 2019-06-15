import os
import string
import logging
import django

from django.conf import settings
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
    """This is the managemant command to add a plugin from a template to a Django application.

    Beware: the "startplugin" management command inherits from TemplateCommand, which is not part of Django's
    official API. There is no guarantee that Django keeps this class stable."""

    # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's _name.
    # If there is a better way to do that - please let me know.
    _django_root: str = settings.ROOT_URLCONF.split(".")[0]

    # absolute path to internal plugins of application
    plugin_path = os.path.join(settings.BASE_DIR, *PluginManager.group.split("."))

    help = (
        "Creates a basic GDAPS plugin structure in the "
        "'{}/' directory from a template.".format(plugin_path)
    )

    missing_args_message = "You must provide a plugin name."

    def handle(self, name, **options):
        self.rewrite_template_suffixes += (
            ("md-tpl", "md"),
            ("in-tpl", "in"),
            ("cfg-tpl", "cfg"),
        )
        from django.core.validators import validate_email

        plugin_path = PluginManager.plugin_path()
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
        self.stdout.write("".join(options["files"]))

        options["upper_cased_app_name"] = name.upper()

        options["project_name"] = self._django_root
        options["plugin_path"] = plugin_path
        options["project_title"] = self._django_root.capitalize()
        options["plugin_group"] = PluginManager.group
        options["files"] += ("MANIFEST.in", "setup.cfg")
        options["extensions"] += ("md", "rst", "txt")
        options["django_version"] = django.get_version()

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

            if os.path.exists(os.path.join(settings.BASE_DIR, "frontend")):
                #  if there is a global "frontend" directory, assume that plugin needs one too and create it.
                os.makedirs(os.path.join(target, "frontend"))

        except OSError as e:
            raise CommandError(e)

        super().handle("app", name, target, template=template, **options)

        self.stdout.write(
            "Please adapt '%s' to your needs.\n"
            % os.path.join(settings.BASE_DIR, target, "setup.cfg")
        )
