"""Module for handling consistent state storage.

Attributes:
    state_file(str): file path where state storage is kept. By default XDG conventions are used. (Most likely ~/.config/python-cozify/python-cozify.cfg)
    state(configparser.ConfigParser): State object used for in-memory state. By default initialized with _initState.
"""

import configparser
import os
import datetime
from absl import logging


def _initXDG():
    """Initialize config path per XDG basedir-spec and resolve the final location of state file storage.

    Returns:
        str: file path to state file as per XDG spec and current env.
    """

    # per the XDG basedir-spec we adhere to $XDG_CONFIG_HOME if it's set, otherwise assume $HOME/.config
    xdg_config_home = ''
    if 'XDG_CONFIG_HOME' in os.environ:
        xdg_config_home = os.environ['XDG_CONFIG_HOME']
        logging.debug('XDG basedir overriden: {0}'.format(xdg_config_home))
    else:
        xdg_config_home = "%s/.config" % os.path.expanduser('~')

    # XDG base-dir: "If, when attempting to write a file, the destination directory is non-existant an attempt should be made to create it with permission 0700. If the destination directory exists already the permissions should not be changed."
    if not os.path.isdir(xdg_config_home):
        logging.debug('XDG basedir does not exist, creating: {0}'.format(xdg_config_home))
        os.mkdir(xdg_config_home, 0o0700)

    # finally create our own config dir
    config_dir = "%s/%s" % (xdg_config_home, 'python-cozify')
    if not os.path.isdir(config_dir):
        logging.debug('XDG local dir does not exist, creating: {0}'.format(config_dir))
        os.mkdir(config_dir, 0o0700)

    state_file = "%s/python-cozify.cfg" % config_dir
    logging.debug('state_file determined to be: {0}'.format(state_file))
    return state_file


def stateWrite(tmpstate=None):
    """Write current state to file storage.

    Args:
        tmpstate(configparser.ConfigParser): State object to store instead of default state.
    """
    global state_file
    if tmpstate is None:
        global state
        tmpstate = state
    with open(state_file, 'w') as cf:
        tmpstate.write(cf)


def setStatePath(filepath=_initXDG(), copy_current=False):
    """Set state storage path. Useful for example for testing without affecting your normal state. Call with no arguments to reset back to autoconfigured location.

    Args:
        filepath(str): file path to use as new storage location. Defaults to XDG defined path.
        copy_current(bool): Instead of initializing target file, dump previous state into it.
    """
    global state_file
    global state
    state_file = filepath
    if copy_current:
        stateWrite()
    else:
        state = _initState(state_file)


def dump_state():
    """Print out current state file to stdout. Long values are truncated since this is only for visualization.
    """
    for section in state.sections():
        print('[{!s:.10}]'.format(section))
        for option in state.options(section):
            print('  {!s:<13.13} = {!s:>10.100}'.format(option, state[section][option]))


def _iso_now():
    """Helper to return isoformat datetime stamp that's more compatible than the default.
    Once Python 3.6 is more widely popular this becomes redundant since isoformat() will support timespec.

    Returns:
        str: now() in isoformat truncated to full seconds.
    """

    return datetime.datetime.now().isoformat().split(".")[0]


def _initState(state_file):
    """Initialize state on cold start. Any stored state is read in or a new basic state is initialized.

    Args:
        state_file(str): State storage filepath to attempt to read from.
    Returns:
        configparser.ConfigParser: State object.
    """
    # if we can read it, read it in, otherwise create empty file
    state = configparser.ConfigParser(allow_no_value=True)
    try:
        cf = open(state_file, 'r')
    except IOError:
        cf = open(state_file, 'w+')
        os.chmod(state_file, 0o600)  # set to user readwrite only to protect tokens
    else:
        state.read_file(cf)

    # make sure config is in roughly a valid state
    for key in ['Cloud', 'Hubs']:
        if key not in state:
            state[key] = {}
    stateWrite(state)
    return state


state_file = _initXDG()
state = _initState(state_file)
