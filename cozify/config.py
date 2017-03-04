import configparser
import os

stateFile = "%s/.config/python-cozify.cfg" % os.path.expanduser('~')
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
