"""Module for all Cozify Hub API 1:1 calls

Attributes:
    apiPath(str): Hub API endpoint path including version. Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.
"""

import requests
import json
from absl import logging

from cozify import cloud_api

from .Error import APIError, ConnectionError

apiPath = '/cc/1.14'


def _getBase(host, port=8893, **kwargs):
    return 'http://{0}:{1}'.format(host, port)


def get(call, hub_token_header=True, base=apiPath, **kwargs):
    """GET method for calling hub API.

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        hub_token_header(bool): Set to False to omit hub_token usage in call headers.
        base(str): Base path to call from API instead of global apiPath. Defaults to apiPath.
        **host(str): ip address or hostname of hub.
        **hub_token(str): Hub authentication token.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=requests.get,
        call='{0}{1}'.format(base, call),
        hub_token_header=hub_token_header,
        **kwargs)


def put(call, data, hub_token_header=True, base=apiPath, **kwargs):
    """PUT method for calling hub API. For rest of kwargs parameters see get()

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        data(str): json string to push out as the payload.
        hub_token_header(bool): Set to False to omit hub_token usage in call headers.
        base(str): Base path to call from API instead of global apiPath. Defaults to apiPath.
    """
    return _call(
        method=requests.put,
        call='{0}{1}'.format(base, call),
        hub_token_header=hub_token_header,
        data=data,
        **kwargs)


def _call(*, call, method, hub_token_header, data=None, **kwargs):
    """Backend for get & put

    Args:
        call(str): Full API path to call.
        method(function): requests.get|put function to use for call.
    """
    response = None
    headers = {}
    if 'headers' in kwargs:
        raise ValueError('Headers already defined: {}'.format(kwargs['headers']))
    if hub_token_header:
        if 'hub_token' not in kwargs:
            raise AttributeError('Asked to do a call to the hub but no hub_token provided.')
        headers['Authorization'] = kwargs['hub_token']
    if data is not None:
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

    if 'remote' in kwargs and kwargs['remote']:  # remote call
        if 'cloud_token' not in kwargs:
            raise AttributeError('Asked to do remote call but no cloud_token provided.')
        headers['Authorization'] = kwargs['cloud_token']
        headers['X-Hub-Key'] = kwargs['hub_token']
        response = cloud_api.remote(apicall=call, data=data, headers=headers)
    else:  # local call
        if 'host' not in kwargs or not kwargs['host']:
            raise AttributeError(
                'Local call but no hostname was provided. Either set keyword remote or host.')
        try:
            response = method(_getBase(**kwargs) + call, headers=headers, data=data, timeout=5)
        except requests.exceptions.RequestException as e:  # pragma: no cover
            raise ConnectionError(str(e)) from None

    # evaluate response, wether it was remote or local
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 410:
        raise APIError(response.status_code,
                       'API version outdated. Update python-cozify. %s - %s - %s' %
                       (response.reason, response.url, response.text))  # pragma: no cover
    else:
        raise APIError(response.status_code,
                       '%s - %s - %s' % (response.reason, response.url, response.text))


def hub(**kwargs):
    """1:1 implementation of /hub API call. For kwargs see cozify.hub_api.get()

    Returns:
        dict: Hub state dict.
    """
    return get('hub', base='/', hub_token_header=False, **kwargs)


def tz(**kwargs):
    """1:1 implementation of /hub/tz API call. For kwargs see cozify.hub_api.get()

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """
    return get('/hub/tz', **kwargs)


def devices(**kwargs):
    """1:1 implementation of /devices API call. For remaining kwargs see cozify.hub_api.get()

    Args:
        **mock_devices(dict): If defined, returned as-is as if that were the result we received.

    Returns:
        dict: Full live device state as returned by the API
    """
    if 'mock_devices' in kwargs:
        return kwargs['mock_devices']

    return get('/devices', **kwargs)


def devices_command(command, **kwargs):
    """1:1 implementation of /devices/command. For kwargs see cozify.hub_api.put()

    Args:
        command(dict): dictionary of type DeviceData containing the changes wanted. Will be converted to json.

    Returns:
        str: What ever the API replied or raises an APIEerror on failure.
    """
    logging.debug('command json to send: {0}'.format(command))
    return put('/devices/command', command, **kwargs)


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
