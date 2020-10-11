"""Support for EE Brightbox router."""
import logging

from eebrightbox import EERouter, EERouterException
import voluptuous as vol

from homeassistant.components.device_tracker import (
    DOMAIN,
    PLATFORM_SCHEMA,
    DeviceScanner,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_VERSION = "version"

CONF_DEFAULT_IP = "192.168.1.254"
CONF_DEFAULT_USERNAME = "admin"
CONF_DEFAULT_VERSION = 3

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_VERSION, default=CONF_DEFAULT_VERSION): cv.positive_int,
        vol.Required(CONF_HOST, default=CONF_DEFAULT_IP): cv.string,
        vol.Required(CONF_USERNAME, default=CONF_DEFAULT_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


def get_scanner(hass, config):
    """Return a router scanner instance."""
    scanner = EEBrightBoxScanner(config[DOMAIN])

    return scanner if scanner.check_config() else None


class EEBrightBoxScanner(DeviceScanner):
    """Scan EE Brightbox router."""

    def __init__(self, config):
        """Initialise the scanner."""
        self.config = config
        self.devices = {}

    def check_config(self):
        """Check if provided configuration and credentials are correct."""
        try:
            with EERouter(self.config) as ee_brightbox:
                return bool(ee_brightbox.get_devices())
        except EERouterException:
            _LOGGER.exception("Failed to connect to the router")
            return False

    def scan_devices(self):
        """Scan for devices."""
        with EERouter(self.config) as ee_brightbox:
            self.devices = {d["mac"]: d for d in ee_brightbox.get_devices()}

        macs = [d["mac"] for d in self.devices.values() if d["activity_ip"]]

        _LOGGER.debug("Scan devices %s", macs)

        return macs

    def get_device_name(self, device):
        """Get the name of a device from hostname."""
        if device in self.devices:
            return self.devices[device]["hostname"] or None

        return None

    def get_extra_attributes(self, device):
        """
        Get the extra attributes of a device.
        Extra attributes include:
        - ip
        - mac
        - port - ethX or wifiX
        - last_active
        """
        port_map = {
            "ath0": "wifi5Ghz",
            "ath1": "wifi2.4Ghz",
            "eth0_0": "eth0",
            "eth0_1": "eth1",
            "eth0_2": "eth2",
            "eth0_3": "eth3",
        }

        if device in self.devices:
            return {
                "ip": self.devices[device]["ip"],
                "mac": self.devices[device]["mac"],
                "port": port_map[self.devices[device]["port"]],
                "last_active": self.devices[device]["time_last_active"],
            }

        return {}