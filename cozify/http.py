"""Helper module for hub_api & cloud_api

Attributes:
    session(requests.Session): Global session used for communications.
"""

import requests, json, jwt, os
from .Error import APIError
from jwt.exceptions import DecodeError
from requests.exceptions import RequestException
from urllib3.exceptions import TimeoutError, ConnectTimeoutError
from absl import logging

from cozify import config

session = requests.Session()
if 'TRAVIS' in os.environ:
    session.trust_env = False
if 'Proxies' in config.state:
    session.proxies = dict(config.state['Proxies'])
    logging.warn('Proxies in use: {0}'.format(session.proxies))
session.timeout = 10


cloud_base = 'https://cloud2.cozify.fi/ui/0.2/'
hub_http = 'http://'
hub_port = ':8893'
hub_base = '/cc/1.9'

def get(call, *, token, headers=None, params=None, **kwargs):
    """GET method for calling hub or cloud APIs.

    Args:
        call(str): Full API URL.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        params(dict): Any additional URL parameters to pass.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.get,
        call=call,
        token=token,
        headers=headers,
        params=params,
        **kwargs)


def put(call, payload, *, token, headers=None, params=None, **kwargs):
    """PUT method for calling hub or cloud APIs.

    Args:
        call(str): Full API URL.
        payload(str): json string to push out as the payload.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        params(dict): Any additional URL parameters to pass.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.put,
        call=call,
        token=token,
        headers=headers,
        params=params,
        payload=payload,
        **kwargs)

def post(call, *, token, headers=None, payload=None, params=None, **kwargs):
    """POST method for calling hub our cloud APIs.

    Args:
        call(str): Full API URL.
        payload(str): json string to push out as the payload.
        token(str): Either hub_token or cloud_token depending on target of call.
        headers(dict): Any additional headers to add to the call.
        params(dict): Any additional URL parameters to pass.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
    """
    return _call(
        method=session.post,
        call=call,
        token=token,
        headers=headers,
        params=params,
        payload=payload,
        **kwargs)

def _call(*, call, method, token, type=None, headers=None, params=None, payload=None, return_json=True, return_text=False, return_raw=False, **kwargs):
    """Backend for get & put

    Args:
        call(str): Full API URL.
        method(function): session.get|put function to use for call.
        token(str): Either hub_token or cloud_token depending on target of call. If the token isn't needed for the call you can specify None but must then specify argument type.
        type(str): Either: 'cloud' or 'hub'. Only needed if token is not provided. (Can be autodetected from token.)
        headers(dict): Any additional headers to add to the call.
        params(dict): Any additional URL parameters to pass.
        payload(str): json string to push out as any potential payload.
        return_json(bool): Return data interpreted as json. Defaults to True.
        return_text(bool): Return data as plain text. Defaults to False.
        return_raw(bool): Return requests.request object. Defaults to False.
        **remote(bool): If call is to be local or remote (bounced via cloud).
        **hub_token(str): Hub authentication token.
        **cloud_token(str): Cloud authentication token. Only needed if remote = True.
        **base(str): Override automatic base detection with a custom string.
    """
    # Turn our call and kwargs data/metadata into a fully qualified URL and valid headers
    url, headers = _get_url(token=token, type=type, call=call, headers=headers, payload=payload, **kwargs)

    try:
        response = method(url, headers=headers, data=payload, params=params)
    except (RequestException, TimeoutError, ConnectTimeoutError) as e:  # pragma: no cover
        raise APIError('connection failure', 'issues connecting to \'{0}\': {1}'.format(url, e)) from None

    if response.status_code == 200:
        if return_raw:
            return response
        if return_text:
            return response.text
        if return_json:
            return response.json()
    elif response.status_code == 410:
        raise APIError(response.status_code,
                       'API version outdated. Update python-cozify. %s - %s - %s' %
                       (response.reason, response.url, response.text))  # pragma: no cover
    elif response.status_code == 403:
        raise APIError(response.status_code,
                'Auth failure({0}). Headers: {1}, error: {2}'.format(response.url, response.request.headers, response.text))  # pragma: no cover
    else:
        logging.debug('Failed call type: {2}, headers: {0}, params: {3} and payload: {1}'.format(headers, payload, method, params))
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url,
                                                               response.text))

def _get_url(call, headers, **kwargs):
    if headers is None:
        headers = {}
    else:
        headers = kwargs['headers']
    # by default stick the token as auth and override with existing headers
    headers = {**{'Authorization': kwargs['token']}, **headers}

    # any payload is expected to be in json unless overriden with a custom header
    if kwargs['payload'] is not None:
        headers = {**{'content-type': 'application/json'}, **headers}

    # figure out the base needed for the call based on token type and remoteness
    base = ''
    if _is_cloud_token(kwargs['token'], kwargs['type']):
        base = cloud_base
    else:
        hub_base_local = hub_base
        if 'base' in kwargs:  # if overriden
            hub_base_local = kwargs['base']
        if kwargs['remote']:  # remote call
            if 'cloud_token' not in kwargs:
                raise AttributeError('Asked to do remote call but no cloud_token provided.')
            headers['Authorization'] = kwargs['cloud_token']
            headers['X-Hub-Key'] = kwargs['hub_token']
            base = cloud_base + 'hub/remote' + hub_base_local
        else:  # local call
            if 'host' not in kwargs or kwargs['host'] is None:
                raise AttributeError('Asked to do local call but no host provided.')
            base = hub_http + kwargs['host'] + hub_port + hub_base_local

    if not base.startswith('http'):
        raise RuntimeError('Internal error, autodetecting full URL has failed, ended up with base: {0}'.format(base))
    return base + call, headers


def _is_cloud_token(token, type):
    if type is not None:
        if type == 'cloud':
            return True
        else:
            return False
    try:
        meta = jwt.decode(token, verify=False)
    except DecodeError:  # if the token is broken let's claim it's a hub.
        logging.error('An invalid token was encountered, the following behaviour is undefined.')
        return False
    if 'hub_name' in meta:
        return False
    else:
        return True
