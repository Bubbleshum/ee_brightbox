"""
Support for EE Smart Hub router
"""

import logging
import urllib.parse

import requests
from ..calmjs.parse import es5
from ..calmjs.parse.asttypes import Object, VarDecl, Assign
from ..calmjs.parse.walkers import Walker

from . import EERouter
from ..helpers import clean_devices, split_multimac

_LOGGER = logging.getLogger(__name__)


class EESmartHub(EERouter):
    """EE Smart Hub router connector."""
    def __init__(self, config):
        """Initialise the router connector."""
        config_defaults = {'host': '192.168.1.254'}
        config = {**config_defaults, **config}

        self.host = config['host']

    def _get_devices(self):
        """
        :returns: List
        """
        _LOGGER.debug("Getting devices")

        devices = self._request()

        return clean_devices(split_multimac(devices))

    def _request(self):
        """
        :returns: List or None
        """

        endpoint = "http://%s/cgi/cgi_myNetwork.js" % self.host

        try:
            response = requests.get(endpoint)
            _LOGGER.debug("Response %s", response.text)

            tree = es5(response.text)
            known_device_list = []

            # find known_device_list variable
            var_known_device_list = None

            walker = Walker()
            for node in walker.filter(tree, lambda node: isinstance(node, VarDecl)):
                if node.identifier.value == 'known_device_list':
                    var_known_device_list = node

            if var_known_device_list is None:
                raise IndexError('known_device_list variable not found.')

            for object_node in walker.filter(var_known_device_list, lambda node: isinstance(node, Object)):
                known_device_list.append({
                    getattr(node.left, 'value', ''): urllib.parse.unquote(getattr(node.right, 'value', '')).replace(
                        '\'', '')
                    for node in walker.filter(object_node, lambda node: isinstance(node, Assign))
                })

            return known_device_list
        except requests.RequestException:
            _LOGGER.error("Status failed %s", endpoint, exc_info=1)
        except IndexError:
            _LOGGER.error("Parsing failed %s", endpoint, exc_info=1)

        return None