#!/usr/bin/env python3

from cozify import cloud, config

config.setStatePath('/tmp/python-cozify-testing.cfg')

print('needRemote: {0}'.format(cloud._needRemoteToken(True)))
print('needHub: {0}'.format(cloud._needHubToken(True)))
print(cloud.authenticate())
