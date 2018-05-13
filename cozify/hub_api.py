"""Module for all Cozify Hub API 1:1 calls

Attributes:
    api_path(str): Hub API endpoint path including version. Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.
"""

import requests, json, logging

from cozify import cloud_api, http

from .Error import APIError
from requests.exceptions import RequestException

api_path = '/cc/1.9'


def base(*, host, port=8893, path=api_path, **kwargs):
    if host is None:
        return path
    else:
        return 'http://{0}:{1}{2}'.format(host, port, path)


def hub(**kwargs):
    """1:1 implementation of /hub API call. For kwargs see cozify.hub_api.get()

    Returns:
        dict: Hub state dict.
    """
    return http.get(base(path='', **kwargs) + '/hub', token=None, **kwargs)


def tz(**kwargs):
    """1:1 implementation of /hub/tz API call. For kwargs see cozify.hub_api.get()

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """
    return http.get(
        base(**kwargs) + '/hub/tz', token=kwargs['hub_token'], return_text=True, **kwargs)


def colors(**kwargs):
    """1:1 implementation of /hub/colors API call. For kwargs see cozify.hub_api.get()

    Returns:
        list: List of hexadecimal color codes of all defined custom colors.
    """
    return http.get(base(**kwargs) + '/hub/colors', token=kwargs['hub_token'], **kwargs)


def lpd433devices(**kwargs):
    """1:1 implementation of /hub/433devices API call. For kwargs see cozify.hub_api.get()

    Returns:
        list: List of dictionaries describing all 433MHz devices paired with hub.
    """
    return http.get(base(**kwargs) + '/hub/433devices', token=kwargs['hub_token'], **kwargs)


def devices(**kwargs):
    """1:1 implementation of /devices API call. For remaining kwargs see cozify.hub_api.get()

    Args:
        **devs(dict): If defined, returned as-is.

    Returns:
        dict: Full live device state as returned by the API
    """
    if 'devs' in kwargs:
        return kwargs['devs']

    return http.get(base(**kwargs) + '/devices', token=kwargs['hub_token'], **kwargs)


def devices_command(command, **kwargs):
    """1:1 implementation of /devices/command. For kwargs see cozify.hub_api.put()

    Args:
        command(dict): dictionary of type DeviceData containing the changes wanted. Will be converted to json.

    Returns:
        str: What ever the API replied or raises an APIEerror on failure.
    """
    command = json.dumps(command)
    logging.debug('command json to send: {0}'.format(command))
    return http.put(
        base(**kwargs) + '/devices/command',
        command,
        token=kwargs['hub_token'],
        return_text=True,
        **kwargs)


def devices_command_generic(*, device_id, command=None, request_type, **kwargs):
    """Command helper for CMD type of actions.
    No checks are made wether the device supports the command or not. For kwargs see cozify.hub_api.put()

    Args:
        device_id(str): ID of the device to operate on.
        request_type(str): Type of CMD to run, e.g. CMD_DEVICE_OFF
        command(dict): Optional dictionary to override command sent. Defaults to None which is interpreted as { device_id, type }
    Returns:
        str: What ever the API replied or raises an APIError on failure.
    """
    if command is None:
        command = [{"id": device_id, "type": request_type}]
    return devices_command(command, **kwargs)


def devices_command_state(*, device_id, state, **kwargs):
    """Command helper for CMD type of actions.
    No checks are made wether the device supports the command or not. For kwargs see cozify.hub_api.put()

    Args:
        device_id(str): ID of the device to operate on.
        state(dict): New state dictionary containing changes.
    Returns:
        str: What ever the API replied or raises an APIError on failure.
    """
    command = [{"id": device_id, "type": 'CMD_DEVICE', "state": state}]
    return devices_command(command, **kwargs)


def devices_command_on(device_id, **kwargs):
    """Command helper for CMD_DEVICE_ON.

    Args:
        device_id(str): ID of the device to operate on.
    Returns:
        str: What ever the API replied or raises an APIError on failure.
    """
    return devices_command_generic(device_id=device_id, request_type='CMD_DEVICE_ON', **kwargs)


def devices_command_off(device_id, **kwargs):
    """Command helper for CMD_DEVICE_OFF.

    Args:
        device_id(str): ID of the device to operate on.
    Returns:
        str: What ever the API replied or raises an APIException on failure.
    """
    return devices_command_generic(device_id=device_id, request_type='CMD_DEVICE_OFF', **kwargs)
