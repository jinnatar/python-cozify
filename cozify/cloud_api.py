"""Module for handling Cozify Cloud API 1:1 functions

Attributes:
    cloudBase(str): API endpoint including version

"""

import json, requests

from .Error import APIError, AuthenticationError

cloudBase = 'https://cloud2.cozify.fi/ui/0.2/'


def requestlogin(email):  # pragma: no cover
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    payload = {'email': email}
    response = requests.post(cloudBase + 'user/requestlogin', params=payload, timeout=5)
    if response.status_code is not 200:
        raise APIError(response.status_code, response.text)


def emaillogin(email, otp):  # pragma: no cover
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    payload = {'email': email, 'password': otp}

    response = requests.post(cloudBase + 'user/emaillogin', params=payload, timeout=5)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)


def lan_ip():  # pragma: no cover
    """1:1 implementation of hub/lan_ip

    This call will fail with an APIError if the requesting source address is not the same as that of the hub, i.e. if they're not in the same NAT network.
    The above is based on observation and may only be partially true.

    Returns:
        list: List of Hub ip addresses.
    """
    response = requests.get(cloudBase + 'hub/lan_ip', timeout=5)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)


def hubkeys(cloud_token):  # pragma: no cover
    """1:1 implementation of user/hubkeys

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        dict: Map of hub_id: hub_token pairs.
    """
    headers = {'Authorization': cloud_token}
    response = requests.get(cloudBase + 'user/hubkeys', headers=headers, timeout=5)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)


def refreshsession(cloud_token):  # pragma: no cover
    """1:1 implementation of user/refreshsession

    Args:
        cloud_token(str) Cloud remote authentication token.

    Returns:
        str: New cloud remote authentication token. Not automatically stored into state.
    """
    headers = {'Authorization': cloud_token}
    response = requests.get(cloudBase + 'user/refreshsession', headers=headers, timeout=5)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)


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
        response = requests.put(
            cloudBase + 'hub/remote' + apicall, headers=headers, data=payload, timeout=5)
    else:
        response = requests.get(cloudBase + 'hub/remote' + apicall, headers=headers, timeout=5)

    return response
