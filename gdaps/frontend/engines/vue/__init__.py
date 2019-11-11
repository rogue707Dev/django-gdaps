import json
import logging
import os
import shutil
import subprocess

from django.conf import settings
from django.core.management import CommandError
from nltk import PorterStemmer

from gdaps.frontend.api import IFrontendEngine, IPackageManager
from gdaps.frontend.conf import frontend_settings
from gdaps.pluginmanager import PluginManager

logger = logging.getLogger(__name__)

# TODO: use header text replacing instead of manually writing a file.
config_file_header = """
// plugins.js
//
// This is a special file that is created by GDAPS automatically
// using the 'syncplugins' management command.
// It will be overwritten with every run of 'manage.py syncplugin'

"""


class VueEngine(IFrontendEngine):
    name = "vue"
    extensions = ("js",)
    rewrite_template_suffixes = ((".js-tpl", ".js"), (".json-tpl", ".json"))
    extra_files = []
    __package_manager = None
    __stemmed_group = None

    @classmethod
    def _singular_plugin_name(cls, plugin):
        if not cls.__stemmed_group:
            cls.__stemmed_group = PorterStemmer().stem(
                PluginManager.group.replace(".", "-")
            )
        return f"{cls.__stemmed_group}-{plugin.label}"

    @classmethod
    def initialize(cls, frontend_dir: str, package_manager: IPackageManager):
        """Initializes an already created frontend using 'npm/yarn install'.
        """

        cls.__package_manager = package_manager

        if shutil.which(package_manager.name) is None:
            raise CommandError(
                f"'{package_manager.name}' command is not available. Aborting."
            )
        if shutil.which("vue") is None:
            package_manager.installglobal(
                "@vue/cli @vue/cli-service-global", cwd=settings.BASE_DIR
            ),

        # this method can assume that the frontend_path exists
        frontend_path = os.path.join(settings.BASE_DIR, frontend_dir)

        subprocess.check_call(
            f"vue create --packageManager {package_manager.name} --no-git --force {frontend_dir}",
            cwd=settings.BASE_DIR,
            shell=True,
        )

        package_manager.install("webpack-bundle-tracker", cwd=frontend_path)

    @classmethod
    def update_plugins_list(cls) -> None:
        """Updates the list of installed Vue frontend plugins.

        This implementation makes sure that all paths are installed by the package manager,
        to be collected dynamically by webpack.
        """

        # first get a list of plugins which have a frontend part.
        # we ignore gdaps itself and then check for a package.json in the frontend directory of the plugin's dir.
        plugins_with_frontends = []
        for plugin in PluginManager.plugins():
            if plugin.name in ["gdaps", "gdaps.frontend"]:
                continue
            else:
                if os.path.exists(
                    os.path.join(plugin.path, "frontend", "package.json")
                ):
                    plugins_with_frontends.append(plugin)

        global_frontend_path = os.path.join(
            settings.BASE_DIR, frontend_settings.FRONTEND_DIR
        )
        frontend_plugins_path = os.path.join(global_frontend_path, "src", "plugins")
        plugins_file_path = os.path.join(frontend_plugins_path, "plugins.js")
        with open(plugins_file_path, "w") as plugins_file:
            plugins_file.write("export default {\n")
            # check if plugin frontend is listed in global /frontend/plugins.
            # If not, install this plugin frontend package via link
            for plugin in plugins_with_frontends:
                plugin_path = os.path.join(plugin.path, "frontend")

                # replace/update js package version with gdaps plugin version
                with open(
                    os.path.join(plugin_path, "package.json"), "r+", encoding="utf-8"
                ) as plugin_package_file:
                    data = json.load(plugin_package_file)
                    # sync frontend plugin versions to backend
                    data["version"] = plugin.PluginMeta.version

                    plugin_package_file.seek(0)
                    json.dump(data, plugin_package_file, ensure_ascii=False, indent=2)
                    plugin_package_file.truncate()

                # if installed plugin with frontend support is not listed in global package.json,
                # link it to frontend plugins
                # if not plugin.label in os.listdir(frontend_plugins_path):
                logger.info(f" ✓ Installing frontend plugin '{plugin.verbose_name}'")
                try:
                    os.symlink(
                        plugin_path,
                        os.path.join(frontend_plugins_path, plugin.label),
                        target_is_directory=True,
                    )
                except FileExistsError:
                    # recreate link (maybe to another, changed directory?)
                    os.remove(os.path.join(frontend_plugins_path, plugin.label))
                    os.symlink(
                        plugin_path,
                        os.path.join(frontend_plugins_path, plugin.label),
                        target_is_directory=True,
                    )
                plugins_file.write(f"  {plugin.label}: '@/plugins/{plugin.label}',\n")

            plugins_file.write("}\n")
            plugins_file.close()

        # if global plugins list contains an orphaned link to a Js package
        # which is not installed (=listed in INSTALLED_APPS) any more,
        # remove that package link.
        logger.info(
            " ⌛ Searching for orphaned plugins in frontend plugins directory..."
        )
        for link in [
            dir for dir in os.listdir(frontend_plugins_path) if os.path.isdir(dir)
        ]:
            if not plugins_with_frontends or not link in [
                plugin.label for plugin in plugins_with_frontends
            ]:
                # dependency has no corresponding installed plugin any more. Uninstall.
                logger.info(f" ✘ Uninstalling frontend plugin '{link}'")
                os.remove(os.path.join(frontend_plugins_path, link))

        if not os.path.exists(global_frontend_path):
            logger.warning(
                f"Could not find frontend directory '{global_frontend_path}'."
            )
            return
