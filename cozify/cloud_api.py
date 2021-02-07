"""Module for handling Cozify Cloud API 1:1 functions

Attributes:
    cloudBase(str): API endpoint including version

"""

import json
import requests

from .Error import APIError, AuthenticationError, ConnectionError

cloudBase = 'https://cloud2.cozify.fi/ui/0.2'


def get(call, headers=None, base=cloudBase, no_headers=False, json=True, raw=False, **kwargs):
    """GET method for calling hub API.

    Args:
        call(str): API path to call after the base, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or payload.
        json(bool): Assume API will return json and decode it.
    """
    return _call(
        method=requests.get,
        call='{0}{1}'.format(base, call),
        headers=headers,
        no_headers=no_headers,
        json=json,
        raw=raw)


def post(call, headers=None, payload=None, base=cloudBase, no_headers=False, raw=False, **kwargs):
    """PUT method for calling hub API. For rest of kwargs parameters see get()

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        payload(dict): Payload dictionary to POST.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or payload.
    """
    return _call(
        method=requests.post,
        call='{0}{1}'.format(base, call),
        headers=headers,
        params=payload,
        no_headers=no_headers,
        raw=raw)


def put(call, headers=None, payload=None, base=cloudBase, no_headers=False, raw=False, **kwargs):
    """PUT method for calling hub API. For rest of kwargs parameters see get()

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        payload(dict): Payload dictionary to PUT.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or payload.
    """
    return _call(
        method=requests.put,
        call='{0}{1}'.format(base, call),
        headers=headers,
        no_headers=no_headers,
        payload=payload,
        raw=raw)


def requestlogin(email, **kwargs):  # pragma: no cover
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    payload = {'email': email}
    post('/user/requestlogin', payload=payload, **kwargs)


def emaillogin(email, otp, **kwargs):  # pragma: no cover
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    payload = {'email': email, 'password': otp}
    post('/user/emaillogin', payload=payload, **kwargs)


def lan_ip(**kwargs):  # pragma: no cover
    """1:1 implementation of hub/lan_ip

    This call will fail with an APIError if the requesting source address is not the same as that of the hub, i.e. if they're not in the same NAT network.
    The above is based on observation and may only be partially true.

    Returns:
        list: List of Hub ip addresses.
    """
    return list(get('/hub/lan_ip', no_headers=True, **kwargs))


def hubkeys(cloud_token, **kwargs):  # pragma: no cover
    """1:1 implementation of user/hubkeys

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        dict: Map of hub_id: hub_token pairs.
    """
    headers = {'Authorization': cloud_token}
    return get('/user/hubkeys', headers=headers, **kwargs)


def refreshsession(cloud_token, **kwargs):  # pragma: no cover
    """1:1 implementation of user/refreshsession

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        str: New cloud remote authentication token. Not automatically stored into state.
    """
    headers = {'Authorization': cloud_token}
    return get('/user/refreshsession', headers=headers, json=False, **kwargs)


def remote(cloud_token, hub_token, apicall, payload=None, **kwargs):  # pragma: no cover
    """1:1 implementation of 'hub/remote'

    Args:
        cloud_token(str): Cloud remote authentication token.
        hub_token(str): Hub authentication token.
        apicall(str): Full API call that would normally go directly to hub, e.g. '/cc/1.6/hub/colors'
        payload(str): json string to use as payload, changes method to PUT.

    Returns:
        requests.response: Requests response object.
    """

    headers = {'Authorization': cloud_token, 'X-Hub-Key': hub_token}

    if payload:
        return put('/hub/remote' + apicall, headers=headers, payload=payload, raw=True, **kwargs)
    else:
        return get('/hub/remote' + apicall, headers=headers, raw=True, **kwargs)


def _call(*,
          call,
          method,
          headers,
          params=None,
          payload=None,
          no_headers=False,
          json=True,
          raw=False):
    """Backend for get & post

    Args:
        call(str): Full API path to call.
        method(function): requests.get|put function to use for call.
        headers(dict): Header dictionary to pass along to the request.
        params(dict): Params dictionary to POST.
        payload(dict): Payload dictionary to PUT.
        no_headers(bool): Allow calling without headers, payload or args.
        json(bool): Assume API will return json and decode it.
        raw(bool): Do no decoding, return requests.response object.
    """
    if not headers and not payload and not params and not no_headers:
        raise AttributeError(
            'Asked to do a call to the cloud without valid headers, payload or params. This would never work.'
        )

    try:
        if payload:
            response = method(call, headers=headers, data=payload, timeout=5)
        if params:
            response = method(call, headers=headers, params=params, timeout=5)
        else:
            response = method(call, headers=headers, timeout=5)

    except requests.exceptions.RequestException as e:  # pragma: no cover
        raise ConnectionError(str(e)) from None

    if response.status_code == 200:
        if raw:
            return response
        if json:
            return response.json()
        else:
            return response.text

    elif response.status_code == 410:
        raise APIError(
            response.status_code,
            'API version outdated. Update python-cozify. {reason} - {url} - {message}'.format(
                reason=response.reason, url=response.url,
                message=response.text))  # pragma: no cover
    else:
        raise APIError(
            response.status_code, '{reason} - {url} - {message}'.format(
                reason=response.reason, url=response.url, message=response.text))
