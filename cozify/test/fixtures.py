#!/usr/bin/env python3

import os, pytest, tempfile, datetime
import hashlib, json

from absl import logging
from mbtest.server import MountebankServer

from cozify import config, hub

from . import fixtures_devices as dev

@pytest.fixture(scope="module")
def vcr_config():
        return {
                "filter_headers": ["authorization", "X-Hub-Key"],
                "record_mode": "rewrite"
                }

@pytest.fixture
def tmp_cloud():
    obj = lambda: 0
    obj.configfile, obj.configpath = tempfile.mkstemp(suffix='tmp_cloud')
    obj.section = 'Cloud'
    obj.email = 'example@example.com'
    obj.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.
    obj.expiry = datetime.timedelta(days=1)
    obj.now = datetime.datetime.now()
    obj.iso_now = obj.now.isoformat().split(".")[0]
    obj.yesterday = obj.now - datetime.timedelta(days=1)
    obj.iso_yesterday = obj.yesterday.isoformat().split(".")[0]
    config.setStatePath(obj.configpath)
    from cozify import cloud
    cloud._setAttr('email', obj.email)
    cloud._setAttr('remotetoken', obj.token)
    cloud._setAttr('last_refresh', obj.iso_yesterday)
    yield obj
    os.remove(obj.configpath)
    logging.error('exiting, tried to remove: {0}'.format(obj.configpath))


@pytest.fixture
def live_cloud():
    configfile, configpath = tempfile.mkstemp(suffix='live_cloud')
    config.setStatePath(configpath, copy_current=True)
    from cozify import cloud
    yield cloud
    config.setStatePath()
    os.remove(configpath)


@pytest.fixture(scope="session")
def mock_server():
    if 'MBTEST_HOST' in os.environ:
        host = os.environ['MBTEST_HOST']
    else:
        host = 'localhost'
    return MountebankServer(port=2525, host=host)


@pytest.fixture
def tmp_hub(tmp_cloud):
    with Tmp_hub(tmp_cloud) as hub_obj:
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
        pytest.xfail('Cannot run certain device tests, no offline COLOR_HS device to test against.')

    yield dev
    hub.device_state_replace(dev, store)


@pytest.fixture()
def online_device():
    dev = None
    store = None
    devs = hub.devices(capabilities=hub.capability.BRIGHTNESS)
    for i, d in devs.items():
        if d['state']['reachable'] and 'test' in d['name']:
            dev = d
            # store state so it can be restored after tests
            store = d['state'].copy()
            break
    if dev is None:
        pytest.xfail(
            'Cannot run certain device tests, no COLOR_HS device online where name includes \'test\'.'
        )
    logging.info('online_device state before use ({1}): {0}'.format(store, _h6_dict(store)))
    yield dev
    logging.info('online_device state after use, before rollback ({1}): {0}'.format(
        dev['state'], _h6_dict(dev['state'])))
    hub.device_state_replace(dev['id'], store)


class Tmp_hub():
    """Creates a temporary hub section (with test data) in a tmp_cloud
    """

    def __init__(self, tmp_cloud):
        self.id = 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'
        self.name = 'HubbyMcHubFace'
        self.host = '127.0.0.1'
        self.section = 'Hubs.{0}'.format(self.id)
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.

    @pytest.mark.usefixtures("tmp_cloud")
    def __enter__(self):
        config.state.add_section(self.section)
        config.state[self.section]['hubname'] = self.name
        config.state[self.section]['host'] = self.host
        config.state[self.section]['hubtoken'] = self.token
        config.state['Hubs']['default'] = self.id
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        config.setStatePath()

    def devices(self):
        return dev.device_ids, dev.devices

    def states(self):
        return dev.states


def _h6_dict(d):
    j = json.dumps(d)
    w = j.encode('utf8')
    h = hashlib.md5(w)
    return h.hexdigest()[:6]
