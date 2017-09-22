"""Module for handling Cozify Cloud API operations

Attributes:
    cloudBase(string): API endpoint including version

"""

import json, requests, logging

from . import config as c
from . import hub

from .Error import APIError, AuthenticationError

cloudBase='https://cloud2.cozify.fi/ui/0.2/'

def authenticate(trustCloud=True, trustHub=True):
    """Authenticate with the Cozify Cloud and Hub.

    Interactive only when absolutely needed, mostly on the first run.
    By default authentication is run selectively only for the portions needed.

    Authentication is a multistep process:
        - trigger sending OTP to email address
        - perform email login with OTP to acquire cloud token
        - acquire hub information and authenticate with hub with cloud token
        - store hub token for further use

    Args:
        trustCloud(bool): Trust current stored state of cloud auth. Default True.
        trustHub(bool): Trust current stored state of hub auth. Default True.
    """

    if 'email' not in  c.state['Cloud'] or not  c.state['Cloud']['email']:
         c.state['Cloud']['email'] = _getEmail()
         c.stateWrite()
    email = c.state['Cloud']['email']

    if _needRemoteToken(trustCloud):
        try:
            _requestlogin(email)
        except APIError:
            resetState() # a bogus email will shaft all future attempts, better to reset
            raise

        # get OTP from user, not stored anywhere since they have a very short lifetime
        otp = _getotp()
        if not otp:
            message = "OTP unavailable, authentication cannot succeed. This may happen if running non-interactively (closed stdin)."
            logging.critical(message)
            raise AuthenticationError(message)

        try:
            remoteToken = _emaillogin(email, otp)
        except APIError:
            logging.error('OTP authentication has failed.')
            resetState()
            raise

        # save the successful remoteToken
        c.state['Cloud']['remoteToken'] = remoteToken
        c.stateWrite()
    else:
        # remoteToken already fine, let's just use it
        remoteToken = c.state['Cloud']['remoteToken']

    if _needHubToken(trustHub):
        hubIps = _lan_ip()
        hubkeys = _hubkeys(remoteToken)
        if not hubIps:
            raise Exception('No LAN ip returned, is your hub registered?')

        for hubIp in hubIps: # hubIps is returned as a list of all hubs
            hubInfo = hub._hub(hubIp)
            hubId = hubInfo['hubId']
            hubName = hubInfo['name']
            if hubId in hubkeys:
                hubToken = hubkeys[hubId]
            else:
                logging.error('The hub "%s" is not linked to the given account: "%s"' % (hubName, c.state['Cloud']['email']))
                resetState()
                return False

            # if hub name not already known, create named section
            hubSection = 'Hubs.' + hubName
            if hubSection not in c.state:
                c.state[hubSection] = {}
            # if default hub not set, set this hub as the first as the default
            if 'default' not in c.state['Hubs']:
                c.state['Hubs']['default'] = hubName

            # store Hub data under it's named section
            c.state[hubSection]['hubToken'] = hubToken
            c.state[hubSection]['host'] = hubIp
            c.state[hubSection]['hubId'] = hubId # not really used for anything but doesn't hurt
            c.stateWrite()
    return True

def resetState():
    """Reset stored cloud state.
    
    Any further authentication flow will start from a clean slate.
    Hub state is left intact.
    """

    c.state['Cloud'] = {}
    c.stateWrite()

def ping():
    """Test cloud token validity.

    Returns:
        bool: validity of stored token.

    """

    try:
        _hubkeys(c.state['Cloud']['remoteToken']) # TODO(artanicus): see if there's a cheaper API call
    except APIError as e:
        if e.status_code == 401:
            return False
        else:
            raise
    else:
        return True

def refresh():
    """Renew current cloud token and store new token in state.

    This call will only succeed if the current cloud token is still valid.
    A new refreshed token is requested from the API and stored in state.

    Returns:
        bool: Success of refresh attempt.
    """
    try:
        newRemoteToken = _refreshsession(c.state['Cloud']['remoteToken'])
    except APIError as e:
        if e.status_code == 401:
            # too late, our token is already dead
            return False
        else:
            raise
    else:
        c.state['Cloud']['remoteToken'] = newRemoteToken
        c.stateWrite()
        return True



def _needRemoteToken(trust):
    """Validate current remote token and decide if we'll request it during authentication.

    Args:
        trust(bool): Set to False to always decide to renew.

    Returns:
        bool: True to indicate a need to request token.
    """

    # check if we've got a remoteToken before doing expensive checks
    if trust and 'remoteToken' in c.state['Cloud']:
        if c.state['Cloud']['remoteToken'] is None:
            return True
        else: # perform more expensive check
            return not ping()
    return True

def _needHubToken(trust):
    """Validate current hub token and decide if we'll request it during authentication.

    Args:
        trust(bool): Set to False to always decide to renew.

    Returns:
        bool: True to indicate a need to request token.
    """

    # First do quick checks, i.e. do we even have a token already
    if trust and ('default' not in c.state['Hubs'] or 'hubtoken' not in c.state['Hubs.' + c.state['Hubs']['default']]):
        return True
    else: # if we have a token, we need to test if the API is callable
        return not hub.ping()

def _getotp():
    try:
        return input('OTP from your email: ')
    except EOFError: # if running non-interactive or ^d
        return None

def _getEmail():
    return input('Enter your Cozify account email address: ')

def _requestlogin(email):
    """Raw Cloud API call, request OTP to be sent to account email address.

    Args:
        email(str): Email address connected to Cozify account.
    """

    payload = { 'email': email }
    response = requests.post(cloudBase + 'user/requestlogin', params=payload)
    if response.status_code is not 200:
        raise APIError(response.status_code, response.text)

def _emaillogin(email, otp):
    """Raw Cloud API call, request cloud token with email address & OTP.

    Args:
        email(str): Email address connected to Cozify account.
        otp(int): One time passcode.

    Returns:
        str: cloud token
    """

    payload = {
            'email': email,
            'password': otp
    }

    response = requests.post(cloudBase + 'user/emaillogin', params=payload)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of hub/lan_ip
# returns list of hub ip's
# Oddly enough remoteToken isn't needed here and on the flipside doesn't help.
# By testing it seems hub/lan_ip will use the source ip of the request to determine the validity of the request.
# Thus, only if you're making the request from the same public ip (or ip block?) will this call succeed with useful results
def _lan_ip():
    response = requests.get(cloudBase + 'hub/lan_ip')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of user/hubkeys
# remoteToken: cozify Cloud remoteToken
# returns map of hubs: { hubId: hubToken }
def _hubkeys(remoteToken):
    headers = {
            'Authorization': remoteToken
    }
    response = requests.get(cloudBase + 'user/hubkeys', headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of 'refreshsession'
# remoteToken: cozify Cloud remoteToken
# returns new remoteToken, not automatically stored into state
def _refreshsession(remoteToken):
    headers = {
            'Authorization': remoteToken
    }
    response = requests.get(cloudBase + 'user/refreshsession', headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of 'hub/remote'
# remoteToken: cozify Cloud remoteToken
# hubToken: cozify hub token
# apicall: Hub api call to be remotely executed, for example: '/cc/1.4/hub/colors'
# returns what ever is appropriate for the call specified in apicall
def _remote(remoteToken, hubToken, apicall, put=False):
    headers = {
            'Authorization': remoteToken,
            'X-Hub-Key': hubToken
    }
    if put:
        response = requests.put(cloudBase + 'hub/remote' + apicall, headers=headers)
    else:
        response = requests.get(cloudBase + 'hub/remote' + apicall, headers=headers)
    
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)
