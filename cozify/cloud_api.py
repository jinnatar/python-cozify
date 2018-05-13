"""Module for handling Cozify Cloud API 1:1 functions
"""

import json, requests
from absl import logging
from . import http
from .Error import APIError, AuthenticationError


def requestlogin(email):  # pragma: no cover
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    params = {'email': email}
    http.post('user/requestlogin', token=None, type='cloud', params=params)


def emaillogin(email, otp):  # pragma: no cover
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    params = {'email': email, 'password': otp}

    return http.post('user/emaillogin', token=None, type='cloud', params=params, return_text=True)


def lan_ip():  # pragma: no cover
    """1:1 implementation of hub/lan_ip

    This call will fail with an APIError if the requesting source address is not the same as that of the hub, i.e. if they're not in the same NAT network.
    The above is based on observation and may only be partially true.

    Returns:
        list: List of Hub ip addresses.
    """
    return http.get('hub/lan_ip', token=None, type='cloud')


def hubkeys(cloud_token):  # pragma: no cover
    """1:1 implementation of user/hubkeys

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        dict: Map of hub_id: hub_token pairs.
    """
    return http.get('user/hubkeys', token=cloud_token)


def refreshsession(cloud_token):  # pragma: no cover
    """1:1 implementation of user/refreshsession

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        str: New cloud remote authentication token. Not automatically stored into state.
    """
    return http.get('user/refreshsession', token=cloud_token, return_text=True)
