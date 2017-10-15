#!/usr/bin/env python3
from cozify import cloud
from cozify.test import debug

def test_auth_cloud():
    print('Baseline;')
    print('needRemote: {0}'.format(cloud._needRemoteToken(True)))
    print('needHub: {0}'.format(cloud._needHubToken(True)))
    print('Authentication with default trust;')
    print(cloud.authenticate())

def test_auth_hub():
    print('Baseline;')
    print('needRemote: {0}'.format(cloud._needRemoteToken(True)))
    print('needHub: {0}'.format(cloud._needHubToken(True)))
    
    print('Authentication with no hub trust;')
    print(cloud.authenticate(trustHub=False))

if __name__ == "__main__":
    test_auth_cloud()
    test_auth_hub()
