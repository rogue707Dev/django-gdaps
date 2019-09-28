import logging
import os
import shutil
import stat

import django
from django.apps import apps
from django.conf import settings
from django.template import Context
from django.utils.version import get_docs_version

from gdaps.conf import gdaps_settings
from gdaps.frontend import current_engine

# this imported is needed to add the plugin to the ExtensionPoint,
# even if it's not used directly.
from gdaps.frontend.engines import vue
from gdaps.management.templates import TemplateCommand
from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__name__)


class Command(TemplateCommand):
    """This command basically comes from Django's TemplateCommand.

    It creates a Javascript frontend from a boilerplate code."""

    help = "Initializes a Django GDAPS application with a Javascript frontend."

    def handle(self, *args, **options):
        super().handle(*args, **options)
        frontend_dir = os.path.expanduser(gdaps_settings.FRONTEND_DIR)

        # create a frontend/ directory in the Django root
        frontend_path = os.path.abspath((os.path.join(settings.BASE_DIR, frontend_dir)))

        self.rewrite_template_suffixes = current_engine().rewrite_template_suffixes

        self.create_directory(frontend_path)

        # run initialisation of engine
        current_engine().initialize(frontend_path)

        project_name = self._django_root
        project_title = self._django_root.title().replace("_", " ")

        self.context = Context(
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

        self.templates.append(
            os.path.join(
                apps.get_app_config("frontend").path,
                "engines",
                current_engine().name,
                "template",
            )
        )

        self.copy_templates()

        current_engine().update_plugins_list(
            [os.path.join(app.path, "frontend") for app in PluginManager.plugins()]
        )
        # build
        # subprocess.check_call(
        #     "npm run build --prefix {base_dir}/{plugin}/frontend".format(
        #         plugin=target, base_dir=settings.BASE_DIR
        #     ),
        #     shell=True,
        # )

        # ask the user to be sure to copy the static files
        # subprocess.check_call('./manage.py collectstatic'.format(plugin=target, base_dir=settings.BASE_DIR), shell=True)
