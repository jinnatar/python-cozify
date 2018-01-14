"""Module for handling highlevel Cozify Hub operations.

Attributes:
    remote(bool): Selector to treat a hub as being outside the LAN, i.e. calls will be routed via the Cozify Cloud remote call system. Defaults to False.
    autoremote(bool): Selector to autodetect hub LAN presence and flip to remote mode if needed. Defaults to True.
    capability(capability): Enum of known device capabilities. Alphabetically sorted, numeric value not guaranteed to stay constant between versions if new capabilities are added.

"""

import requests, logging
from . import config
from . import cloud
from . import hub_api
from enum import Enum


from .Error import APIError

remote = False
autoremote = True

capability = Enum('capability', 'ALERT BASS BRIGHTNESS COLOR_HS COLOR_LOOP COLOR_TEMP CONTACT DEVICE HUMIDITY LOUDNESS MUTE NEXT ON_OFF PAUSE PLAY PREVIOUS SEEK STOP TEMPERATURE TRANSITION TREBLE TWILIGHT USER_PRESENCE VOLUME')

def getDevices(**kwargs):
    """Deprecated, will be removed in v0.3. Get up to date full devices data set as a dict.

    Args:
        **hub_name(str): optional name of hub to query. Will get converted to hubId for use.
        **hub_id(str): optional id of hub to query. A specified hub_id takes presedence over a hub_name or default Hub. Providing incorrect hub_id's will create cruft in your state but it won't hurt anything beyond failing the current operation.
        **remote(bool): Remote or local query.
        **hubId(str): Deprecated. Compatibility keyword for hub_id, to be removed in v0.3
        **hubName(str): Deprecated. Compatibility keyword for hub_name, to be removed in v0.3

    Returns:
        dict: full live device state as returned by the API

    """
    cloud.authenticate() # the old version of getDevices did more than it was supposed to, including making sure there was a valid connection

    hub_id = _get_id(**kwargs)
    hub_token = token(hub_id)
    cloud_token = cloud.token()
    hostname = host(hub_id)

    if 'remote' not in kwargs:
        kwargs['remote'] = remote

    return devices(capability=None, **kwargs)

def devices(*, capabilities=None, and_filter=False, **kwargs):
    """Get up to date full devices data set as a dict. Optionally can be filtered to only include certain devices.

    Args:
        capabilities(cozify.hub.capability): Single or list of cozify.hub.capability types to filter by, for example: [ cozify.hub.capability.TEMPERATURE, cozify.hub.capability.HUMIDITY ]. Defaults to no filtering.
        and_filter(bool): Multi-filter by AND instead of default OR. Defaults to False.
        **hub_name(str): optional name of hub to query. Will get converted to hubId for use.
        **hub_id(str): optional id of hub to query. A specified hub_id takes presedence over a hub_name or default Hub. Providing incorrect hub_id's will create cruft in your state but it won't hurt anything beyond failing the current operation.
        **remote(bool): Remote or local query.
        **hubId(str): Deprecated. Compatibility keyword for hub_id, to be removed in v0.3
        **hubName(str): Deprecated. Compatibility keyword for hub_name, to be removed in v0.3

    Returns:
        dict: full live device state as returned by the API

    """
    hub_id = _get_id(**kwargs)
    hub_token = token(hub_id)
    cloud_token = cloud.token()
    hostname = host(hub_id)
    if remote not in kwargs:
        kwargs['remote'] = remote

    devs = hub_api.devices(host=hostname, hub_token=hub_token, cloud_token=cloud_token, **kwargs)
    if capabilities:
        if isinstance(capabilities, capability): # single capability given
            logging.debug("single capability {0}".format(capabilities.name))
            return { key : value for key, value in devs.items() if capabilities.name in value['capabilities']['values'] }
        else: # multi-filter
            if and_filter:
                return { key : value for key, value in devs.items() if all(c.name in value['capabilities']['values'] for c in capabilities) }
            else: # or_filter
                return { key : value for key, value in devs.items() if any(c.name in value['capabilities']['values'] for c in capabilities) }
    else: # no filtering
        return devs

def _get_id(**kwargs):
    """Get a hub_id from various sources, meant so that you can just throw kwargs at it and get a valid id.
    If no data is available to determine which hub was meant, will default to the default hub. If even that fails, will raise an AttributeError.

    Args:
        **hub_id(str): Will be returned as-is if defined.
        **hub_name(str): Name of hub.
        hubName(str): Deprecated. Compatibility keyword for hub_name, to be removed in v0.3
        hubId(str): Deprecated. Compatibility keyword for hub_id, to be removed in v0.3
    """
    if 'hub_id' in kwargs or 'hubId' in kwargs:
        logging.debug("Redundant hub._get_id call, resolving hub_id to itself.")
        if 'hub_id' in kwargs:
            return kwargs['hub_id']
        return kwargs['hubId']
    if 'hub_name' in kwargs or 'hubName' in kwargs:
        if 'hub_name' in kwargs:
            return getHubId(kwargs['hub_name'])
        return getHubId(kwargs['hubName'])
    return getDefaultHub()

def getDefaultHub():
    """Return id of default Hub.

    If default hub isn't known, run authentication to make it known.
    """

    if 'default' not in config.state['Hubs']:
        logging.critical('no hub name given and no default known, you should run cozify.authenticate()')
        raise AttributeError
    else:
        return config.state['Hubs']['default']

def getHubId(hub_name):
    """Get hub id by it's name.

    Args:
        hub_name(str): Name of hub to query. The name is given when registering a hub to an account.

    Returns:
        str: Hub id or None if the hub wasn't found.
    """

    for section in config.state.sections():
        if section.startswith("Hubs."):
            logging.debug('Found hub {0}'.format(section))
            if config.state[section]['hubname'] == hub_name:
                return section[5:] # cut out "Hubs."
    return None

def _getAttr(hub_id, attr):
    """Get hub state attributes by attr name.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.
        attr(str): Name of hub attribute to retrieve
    Returns:
        str: Value of attribute or exception on failure.
    """
    section = 'Hubs.' + hub_id
    if section in config.state and attr in config.state[section]:
        return config.state[section][attr]
    else:
        logging.warning('Hub id "{0}" not found in state or attribute {1} not set for hub.'.format(hub_id, attr))
        raise AttributeError

def _setAttr(hub_id, attr, value, commit=True):
    """Set hub state attributes by hub_id and attr name

    Args:
        hub_id(str): Id of hub to store for. The id is a string of hexadecimal sections used internally to represent a hub.
        attr(str): Name of cloud state attribute to overwrite. Attribute will be created if it doesn't exist.
        value(str): Value to store
        commit(bool): True to commit state after set. Defaults to True.
    """
    section = 'Hubs.' + hub_id
    if section in config.state:
        if attr not in config.state[section]:
            logging.info("Attribute {0} was not already in {1} state, new attribute created.".format(attr, section))
        config.state[section][attr] = value
        if commit:
            config.stateWrite()
    else:
        logging.warning('Section {0} not found in state.'.format(section))
        raise AttributeError


def name(hub_id):
    """Get hub name by it's id.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        str: Hub name or None if the hub wasn't found.
    """
    return _getAttr(hub_id, 'hubname')

def host(hub_id):
    """Get hostname of matching hub_id

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        str: ip address of matching hub. Be aware that this may be empty if the hub is only known remotely and will still give you an ip address even if the hub is currently remote and an ip address was previously locally known.
    """
    return _getAttr(hub_id, 'host')

def token(hub_id, new_token=None):
    """Get hub_token of matching hub_id or set a new value for it.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        str: Hub authentication token.
    """
    if new_token:
        _setAttr(hub_id, 'hubtoken', new_token)
    return _getAttr(hub_id, 'hubtoken')

def ping(hub_id=None, hub_name=None, **kwargs):
    """Perform a cheap API call to trigger any potential APIError and return boolean for success/failure. For optional kwargs see cozify.hub_api.get()

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
        hub_token = _getAttr(hub_id, 'hubtoken')
        hub_host = _getAttr(hub_id, 'host')
        cloud_token = config.state['Cloud']['remotetoken']

        # if we don't have a stored host then we assume the hub is remote
        global remote
        if not remote and autoremote and not hub_host:
            remote = True
            logging.debug('Ping determined hub is remote and flipped state to remote.')

        timezone = tz(hub_id)
        logging.debug('Ping performed with tz call, response: {0}'.format(timezone))
    except APIError as e:
        if e.status_code == 401:
            logging.debug(e)
            return False
        else:
            raise
    else:
        return True


def tz(hub_id=None, **kwargs):
    """Get timezone of given hub or default hub if no id is specified. For kwargs see cozify.hub_api.get()

    Args:
    hub_id(str): Hub to query, by default the default hub is used.

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """

    if not hub_id:
        hub_id = getDefaultHub()

    ip = host(hub_id)
    hub_token = token(hub_id)
    cloud_token = cloud.token()

    # if remote state not already set in the parameters, include it
    if remote not in kwargs:
        kwargs['remote'] = remote

    return hub_api.tz(host=ip, hub_token=hub_token, cloud_token=cloud_token, **kwargs)
