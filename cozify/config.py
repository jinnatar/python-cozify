import configparser

config = configparser.ConfigParser()
config.read('main.cfg')

# prime ephemeral storage
try:
    file = open(config['Cloud']['ephemeral'], 'r')
except IOError:
    file = open(config['Cloud']['ephemeral'], 'w')

ephemeral = configparser.ConfigParser()
ephemeral.read(config['Cloud']['ephemeral'])

def ephemeralWrite():
    with open(config['Cloud']['ephemeral'], 'w') as configfile:
        ephemeral.write(configfile)
