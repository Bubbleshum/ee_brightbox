"""
Init.
"""
import logging

_LOGGER = logging.getLogger(__name__)


class EERouter:
    """
    Abstract EE Router class
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

    def get_devices(self):
        """
        Retrieve list of devices (ever) recorded by the router.
        :returns: List of dicts with following keys:
            - mac - XX:XX:XX:XX:XX:XX format
            - hostname
            - port - wl0, wl1, eth0/1/2/3
            - ip - xxx.xxx.xxx.xxx format
            - ipv6
            - ipv6_11
            - time_first_seen - Datetime
            - time_last_active - Datetime
            - activity_ip - True/False
            - activity_ipv6 - True/False
            - activity_ipv6_11 - True/False
            - dhcp_option - likely None
            - name - usually matches hostname or 'Unknown'+mac format
            - os - likely None
            - device - likely None
            - device_oui - likely None
            - device_serial - likely None
            - device_class - likely None
        :raises: AuthenticationException if not authenticated
        """
        devices = self._get_devices()

        _LOGGER.debug('Devices %s', devices)

        return devices

    def get_active_devices(self):
        """
        Retrieve list of active devices connected to router.
        Activity is determined using activity_ip flag.
        :returns: List of dicts with following keys:
            - mac - XX:XX:XX:XX:XX:XX format
            - hostname
            - port - wl0, wl1, eth0/1/2/3
            - ip - xxx.xxx.xxx.xxx format
            - ipv6
            - ipv6_11
            - time_first_seen - Datetime
            - time_last_active - Datetime
            - activity - True/False
            - activity_ip - True/False
            - activity_ipv6 - True/False
            - activity_ipv6_11 - True/False
            - dhcp_option - likely None
            - name - usually matches hostname or 'Unknown'+mac format
            - os - likely None
            - device - likely None
            - device_oui - likely None
            - device_serial - likely None
            - device_class - likely None
        :raises: AuthenticationException if not authenticated
        """
        devices = self._get_devices()
        active_devices = [d for d in devices if d['activity_ip']]

        _LOGGER.debug('Active devices %s', active_devices)

        return active_devices

    def _get_devices(self):
        """
        Implement.
        """
        raise NotImplementedError()