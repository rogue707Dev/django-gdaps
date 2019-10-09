import logging

from gdaps.exceptions import PluginError
from gdaps.frontend.api import IFrontendEngine
from gdaps.frontend.conf import frontend_settings
from gdaps.frontend.engines import vue

default_app_config = "gdaps.frontend.apps.FrontendConfig"
logger = logging.getLogger(__file__)

__current_engine: IFrontendEngine or None = None


def current_engine() -> IFrontendEngine:
    """Returns the current frontend engine."""

    # while this function actually returns a plugin class that mocks IFrontendEngine,
    # it's ok to say it returns one, ducktype style.
    global __current_engine
    if __current_engine:
        return __current_engine

    for engine in IFrontendEngine:
        if engine.name == frontend_settings.FRONTEND_ENGINE:
            __current_engine = engine
            return engine

    raise PluginError(
        "No frontend engine is selected. Please select one in settings.py using GDAPS['FRONTEND_ENGINE']"
    )
