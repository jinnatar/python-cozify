import configparser
import os

# write current state to file storage
# if tmpstate is defined, write that specific state object
def stateWrite(tmpstate=None):
    global state_file
    if tmpstate is None:
        global state
        tmpstate = state
    with open(state_file, 'w') as cf:
        tmpstate.write(cf)

# allow setting the state storage location.
# Useful especially for testing without affecting your normal state
def setStatePath(filepath):
    global state_file
    global state
    state_file = filepath
    state = _initState(state_file)



def _initState(state_file):
    # prime state storage
    # if we can read it, read it in, otherwise create empty file
    state = configparser.ConfigParser(allow_no_value=True)
    try:
        cf = open(state_file, 'r')
    except IOError:
        cf = open(state_file, 'w+')
        os.chmod(state_file, 0o600) # set to user readwrite only to protect tokens
    else:
        state.read_file(cf)

    # make sure config is in roughly a valid state
    for key in [ 'Cloud', 'Hubs' ]:
        if key not in state:
            state[key] = {}
    stateWrite(state)
    return state

def _initXDG():
    # per the XDG basedir-spec we adhere to $XDG_CONFIG_HOME if it's set, otherwise assume $HOME/.config
    xdg_config_home = ''
    if 'XDG_CONFIG_HOME' in os.environ:
        xdg_config_home = os.environ['XDG_CONFIG_HOME']
    else:
        xdg_config_home = "%s/.config" % os.path.expanduser('~')

    # XDG base-dir: "If, when attempting to write a file, the destination directory is non-existant an attempt should be made to create it with permission 0700. If the destination directory exists already the permissions should not be changed."
    if not os.path.isdir(xdg_config_home):
        os.mkdir(xdg_config_home, 0o0700)

    # finally create our own config dir
    config_dir = "%s/%s" % (xdg_config_home, 'python-cozify')
    if not os.path.isdir(config_dir):
        os.mkdir(config_dir, 0o0700)

    state_file = "%s/python-cozify.cfg" % config_dir
    return state_file

state_file = _initXDG()
state = _initState(state_file)
