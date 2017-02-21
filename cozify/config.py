import configparser
import os

def ephemeralWrite():
    with open(ephemeralFile, 'w') as configfile:
        ephemeral.write(configfile)

# prime ephemeral storage
ephemeralFile = "%s/.config/python-cozify.cfg" % os.path.expanduser('~')
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
