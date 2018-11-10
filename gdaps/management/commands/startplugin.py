import os
import string
import logging

from django.conf import settings
from gdaps.conf import gdaps_settings
from django.core.exceptions import ValidationError
from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.apps import apps

logger = logging.getLogger(__name__)

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
    _django_root = settings.ROOT_URLCONF.split('.')[0]

    help = "Creates a basic GDAPS plugin structure in the " \
           "'{plugins}/' directory from a template.".format(
        plugins=os.path.join('BASE_DIR/', *gdaps_settings.PLUGIN_PATH.split('.')))

    missing_args_message = "You must provide a plugin _name."

    def handle(self, name, **options):
        from django.core.validators import validate_email

        plugin_path = gdaps_settings.PLUGIN_PATH

        logger.debug('Using plugin directory: {}'.format(plugin_path))

        # override target directory
        target = os.path.join(*plugin_path.split('.'), name)

        if os.path.exists(target):
            raise CommandError("'{}' already exists".format(target))

        # override plugin template directory
        del options['template']
        template = os.path.join(apps.get_app_config('gdaps').path, 'management', 'templates', 'plugin')
        #options['files'] += ['README.md']

        options['upper_cased_app_name'] = name.upper()

        # FIXME: Using ROOT_URLCONF here is a hack to determine the Django project's _name.
        # If there is a better way to do that - please let me know.
        options['project_name'] = self._django_root

        parameters = [
            # key, value, default, validator/None

            ('project_title', 'Human readable Django project title', '', None),
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