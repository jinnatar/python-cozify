#!/usr/bin/env python3
import sys, logging
from cozify import cloud, config

def test_authenticate(conf_file):
    logging.basicConfig(level=logging.DEBUG)
    config.setStatePath(conf_file)
    
    print('Baseline;')
    print('needRemote: {0}'.format(cloud._needRemoteToken(True)))
    print('needHub: {0}'.format(cloud._needHubToken(True)))
    
    print('Authentication with no hub trust;')
    print(cloud.authenticate(trustHub=False))

if __name__ == "__main__":
    conf_file = None
    if len(sys.argv) > 1:
        conf_file = sys.argv[1]
    else:
        conf_file='/tmp/python-cozify-testing.cfg'
    test_authenticate(conf_file)
