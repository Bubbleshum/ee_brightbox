"""
Helpers.
"""

import datetime
import re
import urllib.parse


def parse_to_string(val):
    """
    Convert value to string.
    """
    return parse_to_none(str(val))


def parse_to_integer(val):
    """
    Convert value to integer.
    """
    return parse_to_none(int(val))


def parse_to_boolean(val):
    """
    Convert value to boolean.
    """
    return val in [True, 'True', 'true', 1, '1', 'Yes', 'yes']


def parse_to_datetime(val):
    """
    Convert value to date in YYYY/MM/DD hh:mm:ss format.
    """
    try:
        return datetime.datetime.strptime(val, '%Y/%m/%d %H:%M:%S')
    except ValueError:
        return parse_to_none(val)


def parse_to_none(val):
    """
    Convert value to None if match, pass otherwise.
    """
    if val in ['Unknown', 'NA', '']:
        return None

    return val


def parse_device_db(device_db):
    """
    Parse device_db structure to list of dicts.
    """
    device_re = r"{([^}]*)}"
    prop_re = r"(\w+):'([^']*)'"
    devices = []

    device_items = re.findall(device_re, device_db)

    for device_item in device_items:
        props = re.findall(prop_re, device_item)

        device = {}
        for prop in props:
            device[prop[0]] = urllib.parse.unquote(prop[1])

        devices.append(device)

    return devices


def parse_ssid_value(ssid_value):
    """
    Parse ssid value to a list.
    """
    val_re = r"'([^']*)'"
    ssid = []

    ssid_items = re.findall(val_re, ssid_value)

    for ssid_item in ssid_items:
        ssid.append(urllib.parse.unquote(ssid_item))

    return ssid


def clean(configs, data):
    """
    Cleans data (array of dicts) using configuration of parse functions
    """
    clean_data = []
    for item in data:
        clean_item = {}
        for name, friendly_name, convert_function in configs:
            clean_item[friendly_name] = convert_function(item[name])
        clean_data.append(clean_item)

    return clean_data


def clean_devices(devices):
    """
    Specific implementation to clean devices data.
    """
    device_configs = [
        ('mac', 'mac', parse_to_string),
        ('hostname', 'hostname', parse_to_string),
        ('port', 'port', parse_to_string),
        ('ip', 'ip', parse_to_string),
        ('ipv6', 'ipv6', parse_to_string),
        ('ipv6_ll', 'ipv6_ll', parse_to_string),
        ('time_first_seen', 'time_first_seen', parse_to_datetime),
        ('time_last_active', 'time_last_active', parse_to_datetime),
        ('activity', 'activity', parse_to_boolean),
        ('activity_ip', 'activity_ip', parse_to_boolean),
        ('activity_ipv6', 'activity_ipv6', parse_to_boolean),
        ('activity_ipv6_ll', 'activity_ipv6_ll', parse_to_boolean),
        ('dhcp_option', 'dhcp_option', parse_to_string),
        ('name', 'name', parse_to_string),
        ('os', 'os', parse_to_string),
        ('device', 'device', parse_to_string),
        ('device_oui', 'device_oui', parse_to_string),
        ('device_serial', 'device_serial', parse_to_string),
        ('device_class', 'device_class', parse_to_string),
    ]

    return clean(device_configs, devices)


def clean_ssids(ssids):
    """
    Specific implementation to clean ssids data.
    """
    ssid_configs = [
        ('ssid_ssid', 'ssid', parse_to_string),
        ('ssid_ssidEnable', 'enabled', parse_to_boolean),
        ('ssid_security', 'security', parse_to_integer),
        ('ssid_wpaPassword', 'password', parse_to_string),
        ('ssid_broadcast', 'broadcast', parse_to_boolean),
    ]

    return clean(ssid_configs, ssids)


def split_multimac(devices):
    """
    Router can group device that uses dynamic mac addresses into a single device.
    This function splits them into separate items.
    """
    split_devices = []

    for device in devices:
        if ',' not in device['mac']:
            split_devices.append(device)
            continue

        split_ds = [device.copy() for i in range(len(device['mac'].split(',')))]
        for key, val in device.items():
            if ',' not in val or key not in ('mac', 'activity_ip', 'activity_ipv6', 'activity_ipv6_ll', 'ip', 'port'):
                continue

            for i, split_val in enumerate(val.split(',')):
                split_ds[i][key] = split_val

        for split_d in split_ds:
            split_d['activity'] = split_d['activity_ip']
            split_devices.append(split_d)

    return split_devices