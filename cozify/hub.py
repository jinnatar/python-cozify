"""Module for handling Cozify Hub API operations

Attributes:
    apiPath(string): Hub API endpoint path including version.
    Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.

"""

import requests, json, logging
from . import config as c
from . import cloud

from .Error import APIError

apiPath = '/cc/1.6/'

def getDevices(hubName=None, hubId=None):
    """Get up to date full devices data set as a dict

    Args:
        hubName(str): optional name of hub to query. Defaults to result of ``getDefaultHub()``
        hubId(str): optional id of hub to query. A specified hubId takes presedence over a hubName or default Hub. Providing incorrect hubId's will create cruft in your state but it won't hurt anything beyond failing the current operation.

    Returns:
        dict: full live device state as returned by the API

    """
    # No matter what we got we resolve it down to a hubId
    if not hubId and hubName:
        hubId = getHubId(hubName)
    if not hubName and not hubId:
        hubId = getDefaultHub()

    configName = 'Hubs.' + hubId
    if configName not in c.state or 'hubtoken' not in c.state[configName]:
        logging.warning('No valid authentication token, requesting authentication')
        cloud.authenticate()

    # at this stage we have a valid name and an auth token. We don't know if the token actually works!
    headers = {
        'Content-type': "application/json",
        'Accept': "application/json",
        'Authorization': c.state[configName]['hubtoken'],
        'Cache-control': "no-cache",
    }

    host = c.state[configName]['host']
    response = requests.get(_getBase(host=host) + 'devices', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))

# return name of default Hub
# if default is unknown, run auth to make default known
def getDefaultHub():
    if 'default' not in c.state['Hubs']:
        print('no hub name given and no default known, running authentication')
        cloud.authenticate()
    return c.state['Hubs']['default']

# TODO(artanicus): actually build this function
def getHubId(hubName):
    return c.state['Hubs']['default']

def _getBase(host, port=8893, api=apiPath):
    # TODO(artanicus): this may still need some auth hook
    return 'http://%s:%s%s' % (host, port, api)

# perform a cheap API call to trigger any potential APIError and return boolean for success/failure
def ping(hub_name=None):
    global pings
    if hub_name is None:
        hub_name =  getDefaultHub()
    try:
        config_name = 'Hubs.' + hub_name
        hub_token = c.state[config_name]['hubtoken']
        hub_host = c.state[config_name]['host']
        tz = _tz(hub_host, hub_token)
    except APIError as e:
        if e.status_code == 401:
            return False
        else:
            raise
    else:
        return True


# 1:1 implementation of /hub API call
# hubHost: valid ip/host to hub, defaults to state data
# returns map of hub state
# interestingly enough remoteToken isn't needed here and the hub will answer regardless of auth
def _hub(host):
    response = requests.get(_getBase(host=host, api='/') + 'hub')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of /hub/tz API call
# hubHost: valid ip/host to hub, defaults to state data
# hub_token: authentication token
# returns timezone of hub, e.g. Europe/Helsinki
def _tz(host, hub_token):
    headers = { 'Authorization': hub_token }
    response = requests.get(_getBase(host=host) + 'hub/tz', headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, response.text)
