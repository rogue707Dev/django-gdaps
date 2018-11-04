import os
import string

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.apps import apps

from gdaps.pluginmanager import PluginManager

try:
    # if git is available, make use of git username/email config data
    import git
    reader = git.Repo.init(settings.BASE_DIR).config_reader()
except:
    reader = None


def _snake_case_to_spaces(name):
    return string.capwords(name, '_').replace('_', ' ')


def get_user_data(key):
    if reader:
        return reader.get_value('user', key, default='')
    else:
        return ''


class Command(TemplateCommand):
    help = "Creates a basic GDAPS plugin structure in the " \
           "'plugins/' directory from a template."

    missing_args_message = "You must provide a plugin name."

    def handle(self, name, **options):
        from django.core.validators import validate_email

        # override target directory
        target = os.path.join(PluginManager.plugin_path, name)

        if os.path.exists(target):
            raise CommandError("'{}' already exists".format(target))

        # override plugin template directory
        del options['template']
        template = os.path.join(apps.get_app_config('gdaps').path, 'management', 'templates', 'plugin')
        #options['files'] += ['README.md']

        parameters = [
            # key, value, default, validator/None

            # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's name.
            # If there is a better way to do that - please let me know.
            ('project_name', 'Django project name', settings.ROOT_URLCONF.split('.')[0], None),
            ('project_title', 'Django project title', '', None),
            ('author', 'Author', get_user_data('name'), None),
            ('author_email', 'Email', get_user_data('email'), validate_email),
        ]
        for key, prompt, default, validator in parameters:
            s = ''
            while not s:
                format_str = '{} [{}]: ' if default else '{}: '
                s = input(format_str.format(prompt, default))
                # don't let input string contain a "
                if '"' in s:
                    print('Error: The character \'"\' is not allowed within the string.')
                if default and not s:
                    s = default
                if validator:
                    try:
                        validator(s)
                    except ValidationError as e:
                        print(e.message)
                        s = ''

            options[key] = s

        try:
            os.makedirs(target)
            print('Successfully created plugin directory: {}'.format(target))
        except OSError as e:
            raise CommandError(e)

        super().handle('app', name, target, template=template, **options)

        print('Please adapt \'setup.py\' to your needs.')
