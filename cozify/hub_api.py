"""Module for all Cozify Hub API 1:1 calls

Attributes:
    apiPath(str): Hub API endpoint path including version. Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.
"""

import requests, json, logging, inspect

from functools import wraps

from cozify import cloud_api
from .Error import APIError

apiPath = '/cc/1.6'

def supports_remote(func):
    """Decorator for cleaner implementation of remote routed API calls. Documented args work for any @supports_remote call

    Args:
        remote(bool): If call is to be remote or local.
        cloud_token(str): Cloud authentication token. Only needed if remote connecting via the cloud.
    """
    @wraps(func)
    def wrapper(*args, remote=False, cloud_token=None, **kwargs):
        if remote and cloud_token:
            logging.info("running {0} remotely.".format(func.__name__))
            response = cloud_api.remote(cloud_token=cloud_token, hub_token=kwargs['hub_token'], apicall=apiPath + '/hub/tz')
            print(response)
        else:
            logging.info('Nothing to do')
        return func(*args, **kwargs)
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    params.append(inspect.Parameter(
        'remote',
        inspect.Parameter.KEYWORD_ONLY,
        default = False
        ))
    params.append(inspect.Parameter(
        'cloud_token',
        inspect.Parameter.KEYWORD_ONLY,
        default = None
        ))
    return wrapper

def _getBase(host, port=8893, api=apiPath):
    return 'http://%s:%s%s' % (host, port, api)

def hub(host=None, remoteToken=None, hubToken=None):
    """1:1 implementation of /hub API call

    Args:
        host(str): ip address or hostname of hub
        remoteToken(str): Cloud remote authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.
        hubToken(str): Hub authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.

    Returns:
        dict: Hub state dict converted from the raw json dictionary.
    """

    response = None
    if host:
        response = requests.get(_getBase(host=host, api='/') + 'hub')
    elif remoteToken and hubToken:
        response = cloud._remote(remoteToken, hubToken, '/hub')

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)

@supports_remote
def tz(host, hub_token, cloud_token=None, remote=False):
    """1:1 implementation of /hub/tz API call

    Args:
        host(str): ip address or hostname of hub
        hub_token(str): Hub authentication token.
        cloud_token(str): Cloud authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """

    headers = { 'Authorization': hub_token }
    call = '/hub/tz'
    if not remote:
        response = requests.get(_getBase(host=host) + call, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))


def devices(host, hub_token, remote, cloud_token=None):
    """1:1 implementation of /devices

    Args:
        host(str): ip address or hostname of hub.
        hub_token(str): Hub authentication token.
        remote(bool): If call is to be local or remote.
        cloud_token(str): Cloud authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.
    Returns:
        json: Full live device state as returned by the API

    """

    headers = { 'Authorization': hub_token }
    call = '/devices'
    if remote:
        response = cloud._remote(cloud_token, hub_token, apiPath + call)
    else:
        response = requests.get(_getBase(host=host) + call, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))

def name(host, hub_token, remote, cloud_token=None):
    """1:1 implementation of /hub/name

    Args:
        name(str): New name to give hub
    """
    pass
