"""Module for handling highlevel Cozify Hub operations.

Attributes:
    capability(capability): Enum of known device capabilities. Alphabetically sorted, numeric value not guaranteed to stay constant between versions if new capabilities are added.

"""

import logging
from . import config
from . import hub_api
from enum import Enum


from .Error import APIError

capability = Enum('capability', 'ALERT BASS BATTERY_U BRIGHTNESS COLOR_HS COLOR_LOOP COLOR_TEMP CONTACT CONTROL_LIGHT CONTROL_POWER DEVICE DIMMER_CONTROL GENERATE_ALERT HUMIDITY IDENTIFY LOUDNESS MOISTURE MUTE NEXT ON_OFF PAUSE PLAY PREVIOUS PUSH_NOTIFICATION REMOTE_CONTROL SEEK SMOKE STOP TEMPERATURE TRANSITION TREBLE TWILIGHT USER_PRESENCE VOLUME')

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
    from . import cloud
    cloud.authenticate() # the old version of getDevices did more than it was supposed to, including making sure there was a valid connection

    hub_id = _get_id(**kwargs)
    hub_token = token(hub_id)
    cloud_token = cloud.token()
    hostname = host(hub_id)

    if 'remote' not in kwargs:
        kwargs['remote'] = remote

    return devices(**kwargs)

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
    _fill_kwargs(kwargs)
    devs = hub_api.devices(**kwargs)
    if capabilities:
        if isinstance(capabilities, capability): # single capability given
            return { key : value for key, value in devs.items() if capabilities.name in value['capabilities']['values'] }
        else: # multi-filter
            if and_filter:
                return { key : value for key, value in devs.items() if all(c.name in value['capabilities']['values'] for c in capabilities) }
            else: # or_filter
                return { key : value for key, value in devs.items() if any(c.name in value['capabilities']['values'] for c in capabilities) }
    else: # no filtering
        return devs

def device_toggle(device_id, **kwargs):
    """Toggle power state of any device capable of it such as lamps. Eligibility is determined by the capability ON_OFF.

    Args:
        device_id(str): ID of the device to toggle.
        **hub_id(str): optional id of hub to operate on. A specified hub_id takes presedence over a hub_name or default Hub.
        **hub_name(str): optional name of hub to operate on.
        **remote(bool): Remote or local query.
    """
    _fill_kwargs(kwargs)

    # Get list of devices known to support toggle and find the device and it's state.
    devs = devices(capabilities=capability.ON_OFF, **kwargs)
    dev_state = devs[device_id]['state']
    current_power = dev_state['isOn']
    new_state = _clean_state(dev_state)
    new_state['isOn'] = not current_power # reverse power state
    hub_api.devices_command_state(device_id=device_id, state=new_state, **kwargs)

def device_on(device_id, **kwargs):
    """Turn on a device that is capable of turning on. Eligibility is determined by the capability ON_OFF.
    """
    _fill_kwargs(kwargs)
    if _is_eligible(device_id, capability.ON_OFF, **kwargs):
        hub_api.devices_command_on(device_id, **kwargs)
    else:
        raise AttributeError('Device not found or not eligible for action.')

def device_off(device_id, **kwargs):
    """Turn off a device that is capable of turning off. Eligibility is determined by the capability ON_OFF.
    """
    _fill_kwargs(kwargs)
    if _is_eligible(device_id, capability.ON_OFF, **kwargs):
        hub_api.devices_command_off(device_id, **kwargs)
    else:
        raise AttributeError('Device not found or not eligible for action.')

def _is_eligible(device_id, capability_filter, **kwargs):
    """Check if device matches a AND devices filter.

    Args:
        device_id(str): ID of the device to check.
        filter(): Single hub.capability or a list of them to match against.
    Returns:
        bool: True if filter matches.
    """
    devs = devices(capabilities=capability_filter, **kwargs)
    if device_id in devs:
        return True
    else:
        return False


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
    return default()

def _fill_kwargs(kwargs):
    """Check that common items are present in kwargs and fill them if not.

    Args:
    kwargs(dict): kwargs dictionary to fill. Operated on directly.

    """
    if 'hub_id' not in kwargs:
        kwargs['hub_id'] = _get_id(**kwargs)
    if 'remote' not in kwargs:
        kwargs['remote'] = remote(kwargs['hub_id'])
    if 'autoremote' not in kwargs:
        kwargs['autoremote'] = True
    if 'hub_token' not in kwargs:
        kwargs['hub_token'] = token(kwargs['hub_id'])
    if 'cloud_token' not in kwargs:
        from . import cloud
        kwargs['cloud_token'] = cloud.token()
    if 'host' not in kwargs:
        kwargs['host'] = host(kwargs['hub_id'])

def _clean_state(state):
    """Return purged state of values so only wanted values can be modified.

    Args:
    state(dict): device state dictionary. Original won't be modified.
    """
    out = {}
    for k, v in state.items():
        if isinstance(v, dict): # recurse nested dicts
            out[k] = _clean_state(v)
        elif k == "type": # type values are kept
            out[k] = v
        else: # null out the rest
            out[k] = None
    return out


def getDefaultHub():
    """Deprecated, use default(). Return id of default Hub.
    """
    logging.warn('hub.getDefaultHub is deprecated and will be removed soon. Use hub.default()')
    return default()

def default():
    """Return id of default Hub.

    If default hub isn't known an AttributeError will be raised.
    """

    if 'default' not in config.state['Hubs']:
        logging.critical('Default hub not known, you should run cozify.authenticate()')
        raise AttributeError
    else:
        return config.state['Hubs']['default']

def getHubId(hub_name):
    """Deprecated, use hub_id(). Return id of hub by it's name.

    Args:
        hub_name(str): Name of hub to query. The name is given when registering a hub to an account.
        str: hub_id on success, raises an attributeerror on failure.

    Returns:
        str: Hub id or raises
    """
    logging.warn('hub.getHubId is deprecated and will be removed soon. Use hub.hub_id()')
    return hub_id(hub_name)

def hub_id(hub_name):
    """Get hub id by it's name.

    Args:
        hub_name(str): Name of hub to query. The name is given when registering a hub to an account.

    Returns:
        str: hub_id on success, raises an attributeerror on failure.
    """

    for section in config.state.sections():
        if section.startswith("Hubs."):
            logging.debug('Found hub: {0}'.format(section))
            if config.state[section]['hubname'] == hub_name:
                return section[5:] # cut out "Hubs."
    raise AttributeError('Hub not found: {0}'.format(hub_name))

def _getAttr(hub_id, attr, default=None, boolean=False):
    """Get hub state attributes by attr name. Optionally set a default value if attribute not found.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.
        attr(str): Name of hub attribute to retrieve
        default: Optional default value to set for unset attributes. If no default is provided these raise an AttributeError.
        boolean: Retrieve and return value as a boolean instead of string. Defaults to False.
    Returns:
        str: Value of attribute or exception on failure.
    """
    section = 'Hubs.' + hub_id
    if section in config.state:
        if attr not in config.state[section]:
            if default is not None:
                _setAttr(hub_id, attr, default)
            else:
                raise AttributeError('Attribute {0} not set for hub {1}'.format(attr, hub_id))
        if boolean:
            return config.state.getboolean(section, attr)
        else:
            return config.state[section][attr]
    else:
        raise AttributeError("Hub id '{0}' not found in state.".format(hub_id))

def _setAttr(hub_id, attr, value, commit=True):
    """Set hub state attributes by hub_id and attr name

    Args:
        hub_id(str): Id of hub to store for. The id is a string of hexadecimal sections used internally to represent a hub.
        attr(str): Name of cloud state attribute to overwrite. Attribute will be created if it doesn't exist.
        value(str): Value to store
        commit(bool): True to commit state after set. Defaults to True.
    """
    if isinstance(value, bool):
        value = str(value)

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

def remote(hub_id, new_state=None):
    """Get remote status of matching hub_id or set a new value for it.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        bool: True for a hub considered remote.
    """
    if new_state:
        _setAttr(hub_id, 'remote', new_state)
    return _getAttr(hub_id, 'remote', default=False, boolean=True)

def autoremote(hub_id, new_state=None):
    """Get autoremote status of matching hub_id or set a new value for it.

    Args:
        hub_id(str): Id of hub to query. The id is a string of hexadecimal sections used internally to represent a hub.

    Returns:
        bool: True for a hub with autoremote enabled.
    """
    if new_state:
        _setAttr(hub_id, 'autoremote', new_state)
    return _getAttr(hub_id, 'autoremote', default=True, boolean=True)

def ping(**kwargs):
    """Perform a cheap API call to trigger any potential APIError and return boolean for success/failure. For optional kwargs see cozify.hub_api.get()

    Args:
        **hub_id(str): Hub to ping or default if neither id or name set.
        **hub_name(str): Hub to ping by name.

    Returns:
        bool: True for a valid and working hub authentication state.
    """
    _fill_kwargs(kwargs)
    try:
        if not kwargs['remote'] and kwargs['autoremote'] and not kwargs['host']: # flip state if no host known
            remote(kwargs['hub_id'], True)
            kwargs['remote'] = True
            logging.debug('Ping determined hub is remote and flipped state to remote.')
        timezone = tz(**kwargs)
        logging.debug('Ping performed with tz call, response: {0}'.format(timezone))
    except APIError as e:
        if e.status_code == 401:
            logging.warn(e)
            return False
        else:
            raise
    else:
        return True


def tz(**kwargs):
    """Get timezone of given hub or default hub if no id is specified. For more optional kwargs see cozify.hub_api.get()

    Args:
    **hub_id(str): Hub to query, by default the default hub is used.

    Returns:
        str: Timezone of the hub, for example: 'Europe/Helsinki'
    """
    _fill_kwargs(kwargs)

    return hub_api.tz(**kwargs)
