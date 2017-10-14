"""Module for handling Cozify Hub API operations

Attributes:
    apiPath(string): Hub API endpoint path including version. Things may suddenly stop working if a software update increases the API version on the Hub. Incrementing this value until things work will get you by until a new version is published.
    remote(bool): Selector to treat a hub as being outside the LAN, i.e. calls will be routed via the Cozify Cloud remote call system. Defaults to False.
    autoremote(bool): Selector to autodetect hub LAN presence and flip to remote mode if needed. Defaults to True.

"""

import requests, json, logging
from . import config as c
from . import cloud

from .Error import APIError

apiPath = '/cc/1.6'
remote = False
autoremote = True

def getDevices(hubName=None, hubId=None):
    """Get up to date full devices data set as a dict

    Args:
        hubName(str): optional name of hub to query. Will get converted to hubId for use.
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
    if cloud._needHubToken():
        logging.warning('No valid authentication token, requesting authentication')
        cloud.authenticate()
    hub_token = c.state[configName]['hubtoken']
    cloud_token = c.state['Cloud']['remotetoken']
    host = c.state[configName]['host']

    return _devices(host=host, hub_token=hub_token, cloud_token=cloud_token)

def getDefaultHub():
    """Return id of default Hub.

    If default hub isn't known, run authentication to make it known.
    """

    if 'default' not in c.state['Hubs']:
        logging.warning('no hub name given and no default known, running authentication.')
        cloud.authenticate(remote=remote, autoremote=autoremote)
    return c.state['Hubs']['default']

def getHubId(hub_name):
    """Get hub id by it's name.

    Args:
        hub_name(str): Name of hub to query. The name is given when registering a hub to an account.

    Returns:
        str: Hub id or None if the hub wasn't found.
    """

    for section in c.state.sections():
        if section.startswith("Hubs."):
            logging.debug('Found hub {0}'.format(section))
            if c.state[section]['hubname'] == hub_name:
                return section[5:] # cut out "Hubs."
    return None

def getHubName(hub_id):
    """Get hub name by it's id.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        str: Hub name or None if the hub wasn't found.
    """
    section = 'Hubs.' + hub_id
    if section in c.state and 'hubname' in c.state[section]:
        return c.state[section]['hubname']
    else:
        logging.warning('Hub id "{0}" not found in state.'.format(hub_id))
        return None

def _getBase(host, port=8893, api=apiPath):
    # TODO(artanicus): this may still need some auth hook
    return 'http://%s:%s%s' % (host, port, api)

def ping(hub_id=None, hub_name=None):
    """Perform a cheap API call to trigger any potential APIError and return boolean for success/failure

    Args:
        hub_id(str): Hub to ping or default if None. Defaults to None.
        hub_name(str): Hub to ping or default if None. Defaults to None.

    Returns:
        bool: True for a valid and working hub authentication state.
    """

    if hub_name and not hub_id:
        hub_id = getHubId(hub_name)

    if not hub_id and not hub_name:
        hub_id = getDefaultHub()
    try:
        config_name = 'Hubs.' + hub_id
        hub_token = c.state[config_name]['hubtoken']
        hub_host = c.state[config_name]['host']
        cloud_token = c.state['Cloud']['remotetoken']

        # if we don't have a stored host then we assume the hub is remote
        global remote
        if not remote and autoremote and not hub_host:
            remote = True
            logging.debug('Ping determined hub is remote and flipped state to remote.')

        tz = _tz(hub_host, hub_token, cloud_token)
        logging.debug('Ping performed with tz call, response: {0}'.format(tz))
    except APIError as e:
        if e.status_code == 401:
            logging.debug(e)
            return False
        else:
            raise
    else:
        return True


def _hub(host=None, remoteToken=None, hubToken=None):
    """1:1 implementation of /hub API call

    Args:
        host(str): ip address or hostname of hub
        remoteToken(str): Cloud remote authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.
        hubToken(str): Hub authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.

    Returns:
        dict: Hub state dict converted from the raw json dictionary.
    """

    response = None
    if host:
        response = requests.get(_getBase(host=host, api='/') + 'hub')
    elif remoteToken and hubToken:
        response = cloud._remote(remoteToken, hubToken, '/hub')

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)

# 1:1 implementation of /hub/tz API call
# hubHost: valid ip/host to hub, defaults to state data
# hub_token: authentication token
# returns timezone of hub, e.g. Europe/Helsinki
def _tz(host, hub_token, cloud_token=None):
    """1:1 implementation of /hub/tz API call

    Args:
        host(str): ip address or hostname of hub
        hub_token(str): Hub authentication token.
        cloud_token(str): Cloud authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """

    headers = { 'Authorization': hub_token }
    call = '/hub/tz'
    if remote:
        response = cloud._remote(cloud_token=cloud_token, hub_token=hub_token, apicall=apiPath + call)
    else:
        response = requests.get(_getBase(host=host) + call, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))


def _devices(host, hub_token, cloud_token=None):
    """1:1 implementation of /devices

    Args:
        host(str): ip address or hostname of hub.
        hub_token(str): Hub authentication token.
        cloud_token(str): Cloud authentication token. Only needed if authenticating remotely, i.e. via the cloud. Defaults to None.
    Returns:
        json: Full live device state as returned by the API

    """

    headers = { 'Authorization': hub_token }
    call = '/devices'
    if remote:
        response = cloud._remote(cloud_token, hub_token, apiPath + call)
    else:
        response = requests.get(_getBase(host=host) + call, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise APIError(response.status_code, '%s - %s - %s' % (response.reason, response.url, response.text))
