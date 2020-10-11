"""
Init.
"""
from .router.brightbox2 import EEBrightBox2
from .router.smarthub import EESmartHub
from .errors import (
    EERouterException,
    AuthenticationException,
)


def ee_router_config(config):
    """
    Initialise correct router based on version
    :returns: EERouter
    :raises: EERouterException
    """
    versions = {
        2: EEBrightBox2,
        3: EESmartHub,
    }

    config_defaults = {'version': 2}
    config = {**config_defaults, **config}

    version = int(config['version'])

    if version not in versions:
        raise EERouterException('Unsupported version %s. Only version 2 and 3 is currently supported' % version)

    router_class = versions[version]

    return router_class(config)


# aliases
EEBrightBox = ee_router_config  # deprecated, use EERouter instead
EERouter = ee_router_config