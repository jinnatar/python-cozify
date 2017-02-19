import configparser
import os

# prime ephemeral storage
ephemeralFile = "%s/.config/python-cozify.cfg" % os.path.expanduser('~')
try:
    file = open(ephemeralFile, 'r')
except IOError:
    file = open(ephemeralFile, 'w')

ephemeral = configparser.ConfigParser()
ephemeral.read(ephemeralFile)

def ephemeralWrite():
    with open(ephemeralFile, 'w') as configfile:
        ephemeral.write(configfile)
