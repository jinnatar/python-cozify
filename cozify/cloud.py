"""Module for handling Cozify Cloud highlevel operations.
"""

from absl import logging
import datetime

from . import config
from . import hub_api
from . import cloud_api

from .Error import APIError, AuthenticationError, ConnectionError


def authenticate(trustCloud=True, trustHub=True, remote=False, autoremote=True):
    """Authenticate with the Cozify Cloud and Hub.

    Interactive only when absolutely needed, mostly on the first run.
    By default authentication is run selectively only for the portions needed.
    Hub authentication lives in the Cloud module since the authentication is obtained from
    the cloud.

    Authentication is a multistep process:
        - trigger sending OTP to email address
        - perform email login with OTP to acquire cloud token
        - acquire hub information and authenticate with hub with cloud token
        - store hub token for further use

    Args:
        trustCloud(bool): Trust current stored state of cloud auth. Default True.
        trustHub(bool): Trust current stored state of hub auth. Default True.
        remote(bool): Treat a hub as being outside the LAN, i.e. calls will be routed via the Cozify Cloud remote call system. Defaults to False.
        autoremote(bool): Autodetect hub LAN presence and flip to remote mode if needed. Defaults to True.

    Returns:
        bool: True on authentication success. Failure will result in an exception.
    """

    from . import hub

    if not _isAttr('email'):  # pragma: no cover
        _setAttr('email', _getEmail())
    email = _getAttr('email')

    if _need_cloud_token(trustCloud):  # pragma: no cover
        try:
            cloud_api.requestlogin(email)
        except (APIError, ConnectionError):
            resetState()  # a bogus email will shaft all future attempts, better to reset
            raise

        # get OTP from user, not stored anywhere since they have a very short lifetime
        otp = _getotp()
        try:
            cloud_token = cloud_api.emaillogin(email, otp)
        except (APIError, ConnectionError):
            logging.error('OTP authentication has failed.')
            resetState()
            raise

        # save the successful cloud_token
        _setAttr('last_refresh', config._iso_now(), commit=False)
        _setAttr('remoteToken', cloud_token, commit=True)
    else:
        # cloud_token already fine, let's just use it
        cloud_token = _getAttr('remoteToken')

    if _need_hub_token(trustHub):
        localHubs = cloud_api.lan_ip()  # will only work if we're local to the Hub, otherwise None
        # TODO(artanicus): unknown what will happen if there is a local hub but another one remote. Needs testing by someone with multiple hubs. Issue #7
        hubkeys = cloud_api.hubkeys(
            cloud_token)  # get all registered hubs and their keys from the cloud.
        if not hubkeys:
            logging.fatal(
                'You have not registered any hubs to the Cozify Cloud, hence a hub cannot be used yet.'
            )

        # evaluate all returned Hubs and store them
        for hub_id, hub_token in hubkeys.items():
            logging.debug('hub: {0} token: {1}'.format(hub_id, hub_token))
            hub_info = None
            hub_ip = None

            if not hub.exists(hub_id):
                autoremote = True
            else:
                autoremote = hub.autoremote(hub_id=hub_id)
            # if we're remote, we didn't get a valid ip
            if not localHubs:
                logging.info('No local Hubs detected, changing to remote mode.')
                hub_info = hub_api.hub(remote=True, cloud_token=cloud_token, hub_token=hub_token)
                # if the hub wants autoremote we flip the state. If this is the first time the hub is seen, act as if autoremote=True, remote=False
                if not hub.exists(hub_id) or (hub.autoremote(hub_id) and not hub.remote(hub_id)):
                    logging.info('[autoremote] Flipping hub remote status from local to remote.')
                    remote = True
            else:
                # localHubs is valid so a hub is in the lan. A mixed environment cannot yet be detected.
                # cloud_api.lan_ip cannot provide a map as to which ip is which hub. Thus we actually need to determine the right one.
                # TODO(artanicus): Need to truly test how multihub works before implementing ip to hub resolution. See issue #7
                hub_ip = localHubs[0]
                hub_info = hub_api.hub(host=hub_ip, remote=False)
                # if the hub wants autoremote we flip the state. If this is the first time the hub is seen, act as if autoremote=True, remote=False
                if not hub.exists(hub_id) or (hub.autoremote(hub_id) and hub.remote(hub_id)):
                    logging.info('[autoremote] Flipping hub remote status from remote to local.')
                    remote = False

            hub_name = hub_info['name']
            if hub_id in hubkeys:
                hub_token = hubkeys[hub_id]
            else:  # pragma: no cover
                logging.error('The hub "{0}" is not linked to the given account: "{1}"'.format(
                    hub_name, _getAttr('email')))
                resetState()
                return False

            # if hub name not already known, create named section
            hubSection = 'Hubs.' + hub_id
            if hubSection not in config.state:
                config.state.add_section(hubSection)
            # if default hub not set, set this hub as the first as the default
            if 'default' not in config.state['Hubs']:
                config.state['Hubs']['default'] = hub_id

            # store Hub data under it's named section
            hub._setAttr(hub_id, 'host', hub_ip, commit=False)
            hub._setAttr(hub_id, 'hubName', hub_name, commit=False)
            hub.token(hub_id, hub_token)
            hub.remote(hub_id, remote)
    return True


def resetState():
    """Reset stored cloud state.

    Any further authentication flow will start from a clean slate.
    Hub state is left intact.
    """

    config.state['Cloud'] = {}
    config.stateWrite()


def ping(autorefresh=True, expiry=None):
    """Test cloud token validity. On success will also trigger a refresh if it's needed by the current key expiry.

    Args:
        refresh(bool): Wether to perform a autorefresh check after a successful ping. Defaults to True.
        expiry(datetime.timedelta): timedelta object for duration how often cloud_token will be auto-refreshed when cloud.ping() is called. If not set, cloud.refresh() defaults are used.

    Returns:
        bool: validity of stored token.

    """

    try:
        cloud_api.hubkeys(token())  # TODO(artanicus): see if there's a cheaper API call
    except APIError as e:  # pragma: no cover
        if e.status_code == 401:
            return False
        else:
            raise
    else:
        if expiry:  # pragma: no cover
            refresh(expiry=expiry)
        else:  # let refresh use it's default expiry
            refresh()
        return True


def refresh(force=False, expiry=datetime.timedelta(days=1)):
    """Renew current cloud token and store new token in state.

    This call will only succeed if the current cloud token is still valid.
    A new refreshed token is requested from the API only if sufficient time has passed since the previous refresh.

    Args:
        force(bool): Set to True to always perform a refresh regardless of time passed since previous refresh.
        expiry(datetime.timedelta): timedelta object for duration of refresh expiry. Defaults to one day.

    Returns:
        bool: Success of refresh attempt, True also when expiry wasn't over yet even though no refresh was performed.
    """
    if _need_refresh(force, expiry):
        try:
            cloud_token = cloud_api.refreshsession(token())
        except APIError as e:  # pragma: no cover
            if e.status_code == 401:
                # too late, our token is already dead
                return False
            else:
                raise
        else:
            _setAttr('last_refresh', config._iso_now(), commit=False)
            token(cloud_token)
            logging.info('cloud_token has been successfully refreshed.')

            return True
    else:
        logging.debug(
            "Not refreshing token, it's not old enough yet. Limit is: {0})".format(expiry))


def _need_refresh(force, expiry):
    """Evaluate if refresh timer is already over or if forcing is valid.

    Args:
        force(bool): Set to True to always perform a refresh regardless of time passed since previous refresh.
        expiry(datetime.timedelta): timedelta object for duration of refresh expiry.

    Returns:
        bool: True if refresh should be done according to forcing and expiry.
    """

    last_refresh_str = None

    try:
        last_refresh_str = _getAttr('last_refresh')
    except AttributeError:  # not stored in state yet, e.g. first refresh
        logging.info("Last cloud token refresh unknown, will force refresh.")
        force = True
    else:
        try:
            last_refresh = datetime.datetime.strptime(last_refresh_str, "%Y-%m-%dT%H:%M:%S")
        except ValueError:  # not readable as a timestamp
            logging.error("Last cloud token refresh timestamp invalid, will force refresh.")
            force = True

    now = datetime.datetime.now()

    if force or last_refresh + expiry < now:
        return True


def _need_cloud_token(trust=True):
    """Validate current remote token and decide if we'll request it during authentication.

    Args:
        trust(bool): Set to False to always decide to renew. Defaults to True.

    Returns:
        bool: True to indicate a need to request token.
    """

    # check if we've got a cloud_token before doing expensive checks
    if trust and 'remoteToken' in config.state['Cloud']:
        if config.state['Cloud']['remoteToken'] is None:  # pragma: no cover
            return True
        else:  # perform more expensive check
            return not ping()
    return True


def _need_hub_token(trust=True):
    """Validate current hub token and decide if we'll request it during authentication.

    Args:
        trust(bool): Set to False to always decide to renew. Defaults to True.

    Returns:
        bool: True to indicate a need to request token.
    """
    from . import hub

    if not trust:
        logging.debug("hub_token not trusted so we'll say it needs to be renewed.")
        return True

    # First do quick checks, i.e. do we even have a token already
    if 'default' not in config.state['Hubs'] or 'hubtoken' not in config.state[
            'Hubs.' + config.state['Hubs']['default']]:
        logging.debug("We don't have a valid hubtoken or it's not trusted.")
        return True
    else:  # if we have a token, we need to test if the API is callable
        # avoid compliating things by disabling autorefresh on failure.
        ping = hub.ping(autorefresh=False)
        logging.debug("Testing hub.ping() for hub_token validity: {0}".format(ping))
        return not ping


def _getotp():
    try:
        return input('OTP from your email: ')
    except (EOFError, IOError):  # if running non-interactive or ^d
        message = "OTP unavailable, authentication cannot succeed. This may happen if running non-interactively (closed stdin)."
        raise AuthenticationError(message)


def _getEmail():  # pragma: no cover
    return input('Enter your Cozify account email address: ')


def _getAttr(attr):
    """Get cloud state attributes by attr name

    Args:
        attr(str): Name of cloud state attribute to retrieve
    Returns:
        str: Value of attribute or exception on failure
    """
    section = 'Cloud'
    if section in config.state and attr in config.state[section]:
        return config.state[section][attr]
    else:
        logging.warning('Cloud attribute {0} not found in state.'.format(attr))
        raise AttributeError


def _setAttr(attr, value, commit=True):
    """Set cloud state attributes by attr name

    Args:
        attr(str): Name of cloud state attribute to overwrite. Attribute will be created if it doesn't exist.
        value(str): Value to store
        commit(bool): True to commit state after set. Defaults to True.
    """
    section = 'Cloud'
    if section in config.state:
        if attr not in config.state[section]:
            logging.info(
                "Attribute {0} was not already in {1} state, new attribute created.".format(
                    attr, section))
        config.state[section][attr] = value
        if commit:
            config.stateWrite()
    else:  # pragma: no cover
        logging.warning('Section {0} not found in state.'.format(section))
        raise AttributeError


def _isAttr(attr):
    """Check validity of attribute by attr name.

    Returns:
        bool: True if attribute exists
    """
    return attr in config.state['Cloud'] and config.state['Cloud'][attr]


def token(new_token=None):
    """Get currently used cloud_token or set a new one.

    Returns:
        str: Cloud remote authentication token.
    """
    if new_token:
        _setAttr('remotetoken', new_token)
    return _getAttr('remotetoken')


def email(new_email=None):  # pragma: no cover
    """Get currently used cloud account email or set a new one.

    Returns:
        str: Cloud user account email address.
    """
    if new_email:
        _setAttr('email', new_email)
    return _getAttr('email')
