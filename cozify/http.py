"""Helper module for hub_api & cloud_api

Attributes:
    session(requests.Session): Global session used for communications.
"""

import requests, json, logging
from .Error import APIError
from requests.exceptions import RequestException

session = requests.Session()

def get(call, *, token, headers=None, **kwargs):
    """GET method for calling hub or cloud APIs.

    Args:
        call(str): Full API URL.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.get,
        call=call,
        token=token,
        headers=headers,
        **kwargs)


def put(call, payload, *, token, headers=None, **kwargs):
    """PUT method for calling hub or cloud APIs.

    Args:
        call(str): Full API URL.
        payload(str): json string to push out as the payload.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.put,
        call=call,
        token=token,
        headers=headers,
        payload=payload,
        **kwargs)

def post(call, payload, *, token, headers=None, **kwargs):
    """POST method for calling hub our cloud APIs.

    Args:
        call(str): Full API URL.
        payload(str): json string to push out as the payload.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.post,
        call=call,
        token=token,
        headers=headers,
        payload=payload,
        **kwargs)

def _call(*, call, method, token, headers=None, payload=None, return_data=True, **kwargs):
    """Backend for get & put

    Args:
        call(str): Full API URL.
        method(function): session.get|put function to use for call.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        payload(str): json string to push out as any potential payload.
        return_data(bool): Return only decoded data, not a requests.response object. Defaults to True.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **hub_token(str): Hub authentication token.
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    response = None
    if headers is None:
        headers = {}
    headers = {**{'Authorization': token}, **headers}

    if payload is not None:
        headers['content-type'] = 'application/json'

    if 'remote' not in kwargs:  # Cloud calls won't have it set
        kwargs['remote'] = False  # and won't care what the value is
    if kwargs['remote']:  # remote call
        del headers # we have the wrong token there
        kwargs['remote'] = False  # Doesn't make sense for direct cloud calls
        if 'cloud_token' not in kwargs:
            raise AttributeError('Asked to do remote call but no cloud_token provided.')
        if 'hub_token' not in kwargs:
            raise AttributeError('Asked to do remote call but no hub_token provided.')
        from . import cloud_api
        response = cloud_api.remote(apicall=call, payload=payload, **kwargs)
    else:  # direct call
        try:
            response = method(call, headers=headers, data=payload)
        except RequestException as e:  # pragma: no cover
            raise APIError('connection failure', 'issues connection to \'{0}\': {1}'.format(call, e))

    # evaluate response, wether it was remote or local
    if response.status_code == 200:
        if return_data:
            return response.json()
        else:
            return response
    elif response.status_code == 410:
        raise APIError(response.status_code,
                       'API version outdated. Update python-cozify. %s - %s - %s' %
                       (response.reason, response.url, response.text))  # pragma: no cover
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url,
                                                               response.text))


