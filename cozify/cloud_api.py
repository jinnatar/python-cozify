"""Module for handling Cozify Cloud API 1:1 functions

Attributes:
    cloudBase(str): API endpoint including version

"""

import json
import requests

from .Error import APIError, AuthenticationError, ConnectionError

cloudBase = 'https://cloud2.cozify.fi/ui/0.2'


def get(call,
        headers=None,
        base=cloudBase,
        no_headers=False,
        json_output=True,
        raw=False,
        **kwargs):
    """GET method for calling hub API.

    Args:
        call(str): API path to call after the base, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or data.
        json_output(bool): Assume API will return json and decode it.
    """
    return _call(method=requests.get,
                 call='{0}{1}'.format(base, call),
                 headers=headers,
                 no_headers=no_headers,
                 json_output=json_output,
                 raw=raw,
                 **kwargs)


def post(call, headers=None, data=None, base=cloudBase, no_headers=False, raw=False, **kwargs):
    """PUT method for calling hub API. For rest of kwargs parameters see get()

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        data(dict): Payload dictionary to POST.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or data.
    """
    return _call(method=requests.post,
                 call='{0}{1}'.format(base, call),
                 headers=headers,
                 data=data,
                 no_headers=no_headers,
                 raw=raw,
                 **kwargs)


def put(call, headers=None, data=None, base=cloudBase, no_headers=False, raw=False, **kwargs):
    """PUT method for calling hub API. For rest of kwargs parameters see get()

    Args:
        call(str): API path to call after apiPath, needs to include leading /.
        headers(dict): Header dictionary to pass along to the request.
        data(dict): Payload dictionary to PUT.
        base(str): Base path to call from API instead of global base. Defaults to cloudBase.
        no_headers(bool): Allow calling without headers or data.
    """
    return _call(method=requests.put,
                 call='{0}{1}'.format(base, call),
                 headers=headers,
                 no_headers=no_headers,
                 data=data,
                 raw=raw,
                 **kwargs)


def requestlogin(email, **kwargs):  # pragma: no cover
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    payload = {'email': email}
    post('/user/requestlogin', data=payload, **kwargs)


def emaillogin(email, otp, **kwargs):
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    payload = {'email': email, 'password': otp}
    return post('/user/emaillogin', data=payload, json_output=False, **kwargs)


def lan_ip(**kwargs):
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
    return get('/user/refreshsession', headers=headers, json_output=False, **kwargs)


def remote(apicall, headers, data=None):
    """1:1 implementation of 'hub/remote'

    Args:
        apicall(str): Full API call that would normally go directly to hub, e.g. '/cc/1.6/hub/colors'
        headers(dict): Headers to send with request. Must contain Authorization & X-Hub-Key data.
        data(str): json string to use as payload, changes method to PUT.

    Returns:
        requests.response: Requests response object.
    """

    if data:
        return put('/hub/remote' + apicall, headers=headers, data=data, raw=True)
    else:
        return get('/hub/remote' + apicall, headers=headers, raw=True)


def _call(*,
          call,
          method,
          headers,
          params=None,
          data=None,
          no_headers=False,
          json_output=True,
          raw=False,
          **kwargs):
    """Backend for get & post

    Args:
        call(str): Full API path to call.
        method(function): requests.get|put function to use for call.
        headers(dict): Header dictionary to pass along to the request.
        params(dict): Params dictionary to POST.
        data(dict): Payload dictionary to PUT.
        no_headers(bool): Allow calling without headers, data or args.
        json_output(bool): Assume API will return json and decode it.
        raw(bool): Do no decoding, return requests.response object.
    """
    if not headers and not data and not params and not no_headers:
        raise AttributeError(
            'Asked to do a call to the cloud without valid headers, data or params. This would never work.'
        )

    try:
        if method is requests.put:
            if data:
                response = method(call, headers=headers, data=data, timeout=5)
            else:
                raise AttributeError('PUT call with no data, this would fail!')
        elif params:
            response = method(call, headers=headers, params=params, timeout=5)
        else:
            response = method(call, headers=headers, timeout=5)

    except requests.exceptions.RequestException as e:  # pragma: no cover
        raise ConnectionError(str(e)) from None

    if response.status_code == 200:
        if raw:
            return response
        if json_output:
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
            response.status_code, '{reason} - {url} - {message}'.format(reason=response.reason,
                                                                        url=response.url,
                                                                        message=response.text))
