#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from cozify import cloud, config
from cozify.test import debug

def test_auth_cloud():
    print('Baseline;')
    print('needRemote: {0}'.format(cloud._need_cloud_token(True)))
    print('needHub: {0}'.format(cloud._need_hub_token(True)))
    print('Authentication with default trust;')
    print(cloud.authenticate())

def test_auth_hub():
    print('Baseline;')
    print('needRemote: {0}'.format(cloud._need_cloud_token(True)))
    print('needHub: {0}'.format(cloud._need_hub_token(True)))

    print('Authentication with no hub trust;')
    print(cloud.authenticate(trustHub=False))

class tmp_cloud():
    """Creates a temporary cloud state with test data.
    """
    def __init__(self):
        self.configfile, self.configpath = tempfile.mkstemp()
        self.section = 'Cloud'
        self.email = 'example@example.com'
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg' # valid but useless jwt token.
        self.expiry = datetime.timedelta(days=1)
        self.now = datetime.datetime.now()
        self.iso_now = self.now.isoformat().split(".")[0]
        self.yesterday = self.now - datetime.timedelta(days=1)
        self.iso_yesterday = self.yesterday.isoformat().split(".")[0]
    def __enter__(self):
        config.setStatePath(self.configpath)
        cloud._setAttr('email', self.email)
        cloud._setAttr('remotetoken', self.token)
        cloud._setAttr('last_refresh', self.iso_yesterday)
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.configpath)

        if exc_type is not None:
            debug.logger.error("%s, %s, %s" % (exc_type, exc_value, traceback))
            return False

@pytest.fixture
def tmpcloud(scope='module'):
    with tmp_cloud() as cloud:
        yield cloud

@pytest.fixture
def id(scope='module'):
    return 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'


def test_cloud_refresh_cold(tmpcloud):
    config.state.remove_option('Cloud', 'last_refresh')
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=tmpcloud.expiry)

def test_cloud_refresh_force(tmpcloud):
    config.dump_state()
    assert cloud._need_refresh(force=True, expiry=datetime.timedelta(days=365))

def test_cloud_refresh_expiry_over(tmpcloud):
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(hours=1))

def test_cloud_refresh_expiry_not_over(tmpcloud):
    config.dump_state()
    assert not cloud._need_refresh(force=False, expiry=datetime.timedelta(days=2))
