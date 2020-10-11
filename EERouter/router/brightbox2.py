"""
Support for EE Brightbox 2 router
"""

import hashlib
import logging
import re
import xml.etree.ElementTree as ET

import requests

from . import EERouter
from ..errors import AuthenticationException
from ..helpers import parse_device_db
from ..helpers import parse_ssid_value
from ..helpers import clean_devices
from ..helpers import clean_ssids

_LOGGER = logging.getLogger(__name__)


class EEBrightBox2(EERouter):
    """EE Brightbox 2 router connector."""
    def __init__(self, config):
        """Initialise the router connector."""
        config_defaults = {'host': '192.168.1.1', 'username': 'admin'}
        config = {**config_defaults, **config}

        self.host = config['host']
        self.username = config['username']
        self.password_hash = hashlib.md5(config['password'].encode('utf-8')).hexdigest()

        self.cookies = {}

    def __enter__(self):
        if not self.authenticate():
            raise AuthenticationException('Failed to authenticate')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.forget()

        return exc_type is None

    def authenticate(self):
        """
        Authenticate using username and password.
        :returns: True/False
        """
        _LOGGER.debug("Authenticating %s", self.username)

        endpoint = "http://%s/login.cgi" % self.host
        response = requests.post(endpoint,
                                 cookies=self.cookies,
                                 data={
                                     'usr': self.username,
                                     'pws': self.password_hash,
                                     'GO': 'status.htm',
                                 })

        urn_re = r"new_urn\ \=\ '(.*)'"
        matches = re.search(urn_re, response.text)

        if matches is None:
            _LOGGER.error("Authentication failed %s", response.text)
            return False

        urn = matches.group(1)
        self.cookies = dict(urn=urn)
        _LOGGER.debug("Authenticated with cookie %s", urn)
        return True

    def is_authenticated(self):
        """
        Check if successfully completed authentication.
        :returns: True/False
        """
        return 'urn' in self.cookies

    def forget(self):
        """
        Perform logout and removes cookies.
        """
        _LOGGER.debug("Logging out")

        endpoint = "http://%s/logout.cgi" % self.host
        requests.post(endpoint, cookies=self.cookies)

        self.cookies = {}

    def get_ssids(self):
        """
        :returns: List of dicts with following keys:
            - ssid
            - enabled - True/False
            - security - int
            - password
            - broadcast - True/False
        """
        _LOGGER.debug("Getting ssid")

        # parse XML and retrieve deviceDB node
        root = self._get_status_conn_xml()

        nodes = ['ssid_ssid', 'ssid_ssidEnable', 'ssid_security', 'ssid_wpaPassword', 'ssid_broadcast']

        ssids = []
        for node_name in nodes:
            node_value = parse_ssid_value(root.find(node_name).get('value'))
            for index, entry in enumerate(node_value):
                try:
                    ssids[index][node_name] = entry
                except IndexError:
                    ssids.append({node_name: entry})

        return [s for s in clean_ssids(ssids) if s['ssid'] is not None]

    def _get_devices(self):
        """
        :returns: List
        """
        _LOGGER.debug("Getting devices")

        # parse XML and retrieve deviceDB node
        root = self._get_status_conn_xml()
        device_db = root.find('deviceDB').get('value')

        # node value is almost-JSON
        devices = parse_device_db(device_db)

        return clean_devices(devices)

    def _get_status_conn_xml(self):
        """
        :returns: ElementTree or None
        """
        if not self.is_authenticated():
            raise AuthenticationException('Not authenticated')

        endpoint = "http://%s/status_conn.xml" % self.host
        try:
            response = requests.get(endpoint, cookies=self.cookies)
            _LOGGER.debug("Response %s", response.text)

            return ET.fromstring(response.text)
        except requests.RequestException:
            _LOGGER.error("Status failed %s", endpoint, exc_info=1)

        return None