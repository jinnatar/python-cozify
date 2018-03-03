#!/usr/bin/env python3

import os, pytest, tempfile, datetime, logging

from cozify import conftest, config, hub, cloud

from . import fixtures_devices as dev

@pytest.fixture
def default_hub():
    barehub = lambda:0
    config.setStatePath() # reset to default config
    config.dump_state()
    barehub.hub_id = hub.default()
    barehub.name = hub.name(barehub.hub_id)
    barehub.host = hub.host(barehub.hub_id)
    barehub.token = hub.token(barehub.hub_id)
    barehub.remote = hub.remote
    return barehub

@pytest.fixture
def tmp_cloud():
    with Tmp_cloud() as cloud:
        yield cloud

@pytest.fixture
def live_cloud():
    config.setStatePath() # reset to default
    return cloud

@pytest.fixture
def id():
    return 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'

@pytest.fixture
def tmphub():
    with tmp_hub() as hub:
        yield hub

@pytest.fixture
def id():
    return 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'

@pytest.fixture
def devices():
    return dev

@pytest.fixture
def livehub(request):
    config.setStatePath() # default config assumed to be live
    config.dump_state() # dump state so it's visible in failed test output
    if hasattr(request, 'param'): # can be specified to toggle use of ping
        autoremote = request.param
    else:
        autoremote = True
    if autoremote:
        logging.debug('Livehub setup checking if connection valid.')
        assert hub.ping()
    else:
        logging.debug('Livehub setup skipped ping.')
    return hub

class Tmp_cloud():
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
            logging.error("%s, %s, %s" % (exc_type, exc_value, traceback))
            return False

class tmp_hub():
    """Creates a temporary hub section (with test data) in a tmp_cloud
    """
    def __init__(self):
        self.id = 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'
        self.name = 'HubbyMcHubFace'
        self.host = '127.0.0.1'
        self.section = 'Hubs.{0}'.format(self.id)
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg' # valid but useless jwt token.
    def __enter__(self):
        self.cloud = Tmp_cloud() # this also initializes temporary state
        config.state.add_section(self.section)
        config.state[self.section]['hubname'] = self.name
        config.state[self.section]['host'] = self.host
        config.state[self.section]['hubtoken'] = self.token
        config.state['Hubs']['default'] = self.id
        print('Temporary state:')
        config.dump_state()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logging.error("%s, %s, %s" % (exc_type, exc_value, traceback))
            return False
        config.state.remove_section(self.section)

    def devices(self):
        return dev.device_ids, dev.devices
