import configparser
import os

ephemeralFile = "%s/.config/python-cozify.cfg" % os.path.expanduser('~')
ephemeral = None


def ephemeralWrite():
    with open(ephemeralFile, 'w') as configfile:
        ephemeral.write(configfile)

# allow setting the ephemeral storage location.
# Useful especially for testing without affecting your normal state
def setStatePath(filepath):
    global ephemeralFile
    ephemeralFile = filepath
    _initState()



def _initState():
    global ephemeral

    # prime ephemeral storage
    try:
        file = open(ephemeralFile, 'r')
    except IOError:
        file = open(ephemeralFile, 'w+')
        os.chmod(ephemeralFile, 0o600) # set to user readwrite only to protect tokens

    ephemeral = configparser.ConfigParser()
    ephemeral.read(ephemeralFile)

    # make sure config is in roughly a valid state
    for key in [ 'Cloud', 'Hubs' ]:
        if key not in ephemeral:
            ephemeral[key] = {}
    ephemeralWrite()

_initState()
