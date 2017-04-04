import configparser
import os

# per the XDG basedir-spec we adhere to $XDG_CONFIG_HOME if it's set, otherwise assume $HOME/.config
xdg-config-home = ''
if 'XDG_CONFIG_HOME' in os.environ:
    xdg-config-home = os.environ['XDG_CONFIG_HOME']
else:
    xdg-config-home = "%s/.config" % os.path.expanduser('~')

# XDG base-dir: "If, when attempting to write a file, the destination directory is non-existant an attempt should be made to create it with permission 0700. If the destination directory exists already the permissions should not be changed."
if not os.path.isdir(xdg-config-home):
    os.mkdir(xdg-config-home, 0700)

# finally create our own config dir
config-dir = "%s/%s" % (xdg-config-home, 'python-cozify')
if not os.path.isdir(config-dir):
    os.mkdir(config-dir, 0o0700)

stateFile = "%s/python-cozify.cfg" % config-dir
state = None


def stateWrite():
    with open(stateFile, 'w') as configfile:
        state.write(configfile)

# allow setting the state storage location.
# Useful especially for testing without affecting your normal state
def setStatePath(filepath):
    global stateFile
    stateFile = filepath
    _initState()



def _initState():
    global state

    # prime state storage
    try:
        file = open(stateFile, 'r')
    except IOError:
        file = open(stateFile, 'w+')
        os.chmod(stateFile, 0o600) # set to user readwrite only to protect tokens

    state = configparser.ConfigParser()
    state.read(stateFile)

    # make sure config is in roughly a valid state
    for key in [ 'Cloud', 'Hubs' ]:
        if key not in state:
            state[key] = {}
    stateWrite()

_initState()
