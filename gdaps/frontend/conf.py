import os
from django.conf import settings
from gdaps.conf import PluginSettings

NAMESPACE = "GDAPS"

DEFAULTS = {
    "FRONTEND_DIR": os.path.join(settings.BASE_DIR, "frontend"),
    "FRONTEND_ENGINE": None,
    "STATS_FILE": os.path.join(settings.BASE_DIR, "frontend", "webpack-stats.json"),
}

frontend_settings = PluginSettings(NAMESPACE, None, DEFAULTS, None)
