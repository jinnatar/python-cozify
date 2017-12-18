"""Module for all Cozify Hub API 1:1 calls

Attributes:
    apiPath(str): Hub API endpoint path including version. Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.
"""

import requests, json

from cozify import cloud_api

from .Error import APIError

apiPath = '/cc/1.6'

def _getBase(host, port=8893, api=apiPath):
    return 'http://%s:%s%s' % (host, port, api)

def _headers(hub_token):
    return { 'Authorization': hub_token }

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
    response = None
    headers = None
    if kwargs['remote'] and kwargs['cloud_token']:
        response = cloud_api.remote(apicall=base + call, **kwargs)
    else:
        if hub_token_header:
            headers = _headers(kwargs['hub_token'])
        response = requests.get(_getBase(host=kwargs['host'], api=base) + call, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))

def hub(**kwargs):
    """1:1 implementation of /hub API call. For kwargs see cozify.cloud_api.get()

    Returns:
        dict: Hub state dict.
    """
    return get('hub', base='/', hub_token_header=False, **kwargs)

def tz(**kwargs):
    """1:1 implementation of /hub/tz API call. For kwargs see cozify.cloud_api.get()

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """
    return get('/hub/tz', **kwargs)

def devices(**kwargs):
    """1:1 implementation of /devices API call. For kwargs see cozify.cloud_api.get()

    Returns:
        json: Full live device state as returned by the API
    """
    return get('/devices', **kwargs)
