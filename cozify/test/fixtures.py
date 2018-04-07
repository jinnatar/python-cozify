#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from absl import logging
from cozify import config, hub

from . import fixtures_devices as dev


@pytest.fixture
def tmp_cloud():
    with Tmp_cloud() as cloud:
        yield cloud


@pytest.fixture
def live_cloud():
    configfile, configpath = tempfile.mkstemp()
    config.setStatePath(configpath, copy_current=True)
    from cozify import cloud
    yield cloud
    config.setStatePath()
    os.remove(configpath)


@pytest.fixture()
def tmp_hub():
    with Tmp_hub() as hub_obj:
        print('Tmp hub state for testing:')
        config.dump_state()
        yield hub_obj


@pytest.fixture()
def live_hub():
    config.setStatePath()  # default config assumed to be live
    print('Live hub state for testing:')
    config.dump_state()  # dump state so it's visible in failed test output
    from cozify import hub
    yield hub


@pytest.fixture()
def offline_device():
    dev = None
    store = None
    for i, d in hub.devices(capabilities=hub.capability.COLOR_HS).items():
        if not d['state']['reachable']:
            dev = i
            # store state so it can be restored after tests
            store = d['state']
            break
    if dev is None:
        logging.fatal('Cannot run device tests, no offline COLOR_HS device to test against.')

    yield dev
    hub.device_state_replace(dev, store)


@pytest.fixture()
def online_device():
    dev = None
    store = None
    devs = hub.devices(capabilities=hub.capability.COLOR_HS)
    for i, d in devs.items():
        if d['state']['reachable'] and 'test' in d['name']:
            dev = d
            # store state so it can be restored after tests
            store = d['state'].copy()
            break
    if dev is None:
        logging.error(
            'Cannot run certain device tests, no COLOR_HS device online where name includes \'test\'.'
        )
    logging.info('Stored state before yield: {0}'.format(store))
    yield dev
    logging.info('Rolling back state of test device')
    hub.device_state_replace(dev['id'], store)


class Tmp_cloud():
    """Creates a temporary cloud state with test data.
    """

    def __init__(self):
        self.configfile, self.configpath = tempfile.mkstemp()
        self.section = 'Cloud'
        self.email = 'example@example.com'
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.
        self.expiry = datetime.timedelta(days=1)
        self.now = datetime.datetime.now()
        self.iso_now = self.now.isoformat().split(".")[0]
        self.yesterday = self.now - datetime.timedelta(days=1)
        self.iso_yesterday = self.yesterday.isoformat().split(".")[0]
        config.setStatePath(self.configpath)
        from cozify import cloud
        cloud._setAttr('email', self.email)
        cloud._setAttr('remotetoken', self.token)
        cloud._setAttr('last_refresh', self.iso_yesterday)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.configpath)

        if exc_type is not None:
            logging.error("%s, %s, %s" % (exc_type, exc_value, traceback))
            return False


class Tmp_hub():
    """Creates a temporary hub section (with test data) in a tmp_cloud
    """

    def __init__(self):
        self.id = 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'
        self.name = 'HubbyMcHubFace'
        self.host = '127.0.0.1'
        self.section = 'Hubs.{0}'.format(self.id)
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.
        self.cloud = Tmp_cloud()  # this also initializes temporary state
        config.state.add_section(self.section)
        config.state[self.section]['hubname'] = self.name
        config.state[self.section]['host'] = self.host
        config.state[self.section]['hubtoken'] = self.token
        config.state['Hubs']['default'] = self.id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        config.setStatePath()

    def devices(self):
        return dev.device_ids, dev.devices

    def states(self):
        return dev.states
