"""Helper module for hub_api & cloud_api
"""

import requests, json, logging

from .Error import APIError
from requests.exceptions import RequestException

def get(call, hub_token_header=True, base=api_path, **kwargs):
    """GET method for calling hub API.

    Args:
        call(str): API path to call after api_path, needs to include leading /.
        hub_token_header(bool): Set to False to omit hub_token usage in call headers. Most calls need this.
        base(str): Base path to call from API instead of global api_path. Defaults to api_path. Most calls need the default.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **host(str): ip address or hostname of hub. Only needed if remote == False.
        **hub_token(str): Hub authentication token.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=requests.get,
        call='{0}{1}'.format(base, call),
        hub_token_header=hub_token_header,
        **kwargs)


def put(call, payload, hub_token_header=True, base=api_path, **kwargs):
    """PUT method for calling hub API.

    Args:
        call(str): API path to call after api_path, needs to include leading /.
        payload(str): json string to push out as the payload.
        hub_token_header(bool): Set to False to omit hub_token usage in call headers.
        base(str): Base path to call from API instead of global api_path. Defaults to api_path. Most calls need the default.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **host(str): ip address or hostname of hub. Only needed if remote == False.
        **hub_token(str): Hub authentication token.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=requests.put,
        call='{0}{1}'.format(base, call),
        hub_token_header=hub_token_header,
        payload=payload,
        **kwargs)


def _call(*, call, method, hub_token_header, payload=None, **kwargs):
    """Backend for get & put

    Args:
        call(str): Full API path to call.
        method(function): requests.get|put function to use for call.
        payload(str): json string to push out as any potential payload.
        hub_token_header(bool): Set to False to omit hub_token usage in call headers.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **host(str): ip address or hostname of hub. Only needed if remote == False.
        **hub_token(str): Hub authentication token.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    response = None
    headers = {}
    if hub_token_header:
        if 'hub_token' not in kwargs:
            raise AttributeError('Asked to do a call to the hub but no hub_token provided.')
        headers['Authorization'] = kwargs['hub_token']
    if payload is not None:
        headers['content-type'] = 'application/json'

    if kwargs['remote']:  # remote call
        if 'cloud_token' not in kwargs:
            raise AttributeError('Asked to do remote call but no cloud_token provided.')
        response = cloud_api.remote(apicall=call, payload=payload, **kwargs)
    else:  # local call
        if not kwargs['host']:
            raise AttributeError(
                'Local call but no hostname was provided. Either set keyword remote or host.')
        try:
            response = method(_getBase(host=kwargs['host']) + call, headers=headers, data=payload)
        except RequestException as e:  # pragma: no cover
            raise APIError('connection failure', 'issues connection to \'{0}\': {1}'.format(
                kwargs['host'], e))

    # evaluate response, wether it was remote or local
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 410:
        raise APIError(response.status_code,
                       'API version outdated. Update python-cozify. %s - %s - %s' %
                       (response.reason, response.url, response.text))  # pragma: no cover
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url,
