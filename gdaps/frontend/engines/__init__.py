from django.core.management import CommandError
from gdaps.frontend import frontend_settings

package_managers = {
    "npm": {
        "name": "npm",
        "init": "npm init",
        "install": "npm install {pkg}",
        "installglobal": "npm install --global {pkg}",
    },
    "yarn": {
        "name": "yarn",
        "init": "yarn init",
        "install": "yarn add {pkg}",
        "installglobal": "yarn global add {pkg}",
    },
}


def current_package_manager() -> dict:
    name = frontend_settings.FRONTEND_PKG_MANAGER
    if not name in package_managers:
        raise CommandError("'FRONTEND_PKG_MANAGER' settings has invalid value.")
    return package_managers[name]
