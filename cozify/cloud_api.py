"""Module for handling Cozify Cloud API 1:1 functions

Attributes:
    base(str): API endpoint including version
"""

import json, requests
from absl import logging
from . import http
from .Error import APIError, AuthenticationError

base = 'https://cloud2.cozify.fi/ui/0.2/'


def requestlogin(email):  # pragma: no cover
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    payload = {'email': email}
    http.post(base + 'user/requestlogin', token=None, payload=payload)


def emaillogin(email, otp):  # pragma: no cover
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    payload = {'email': email, 'password': otp}

    return http.post(base + 'user/emaillogin', token=None, payload=payload)


def lan_ip():  # pragma: no cover
    """1:1 implementation of hub/lan_ip

    This call will fail with an APIError if the requesting source address is not the same as that of the hub, i.e. if they're not in the same NAT network.
    The above is based on observation and may only be partially true.

    Returns:
        list: List of Hub ip addresses.
    """
    return http.get(base + 'hub/lan_ip', token=None)


def hubkeys(cloud_token):  # pragma: no cover
    """1:1 implementation of user/hubkeys

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        dict: Map of hub_id: hub_token pairs.
    """
    return http.get(base + 'user/hubkeys', token=cloud_token)


def refreshsession(cloud_token):  # pragma: no cover
    """1:1 implementation of user/refreshsession

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        str: New cloud remote authentication token. Not automatically stored into state.
    """
    response = http.get(base + 'user/refreshsession', token=cloud_token, return_data=False)
    return response.text


def remote(*, cloud_token, hub_token, apicall, method=http.get, payload=None, **kwargs):
    """1:1 implementation of 'hub/remote'

    Args:
        cloud_token(str): Cloud remote authentication token.
        hub_token(str): Hub authentication token.
        apicall(str): Full API call that would normally go directly to hub, e.g. '/cc/1.6/hub/colors'
        method(function): cozify.http method to use, e.g. http.put. Defaults to http.get.
        payload(str): json string to use as payload, changes method to PUT.

    Returns:
        requests.response: Requests response object.
    """
    headers = {'X-Hub-Key': hub_token}

    if 'cloud_token' not in kwargs:  # needed for the call
        kwargs['cloud_token'] = cloud_token
    if apicall.startswith('http'):  # full URL instead of only api path
        import re
        # strip out http(s)://0.0.0.0:0000
        apicall = re.sub(r'^https?://.*?:[0-9]+', '', apicall)
    return method(
        base + 'hub/remote' + apicall,
        token=cloud_token,
        headers=headers,
        payload=payload,
        return_data=False,
        **kwargs)
