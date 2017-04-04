#!/usr/bin/env python3

from cozify import cloud, config, hub

config.setStatePath('/tmp/python-cozify-testing.cfg')

print(hub.getDevices())
