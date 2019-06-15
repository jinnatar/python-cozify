#!/usr/bin/env python3

import os, pytest, tempfile, datetime
import hashlib, json, jwt

from absl import logging
from cozify import config, hub
from datadiff import diff

from . import fixtures_devices as dev


@pytest.fixture
def tmp_config():
    fh, path = tempfile.mkstemp(suffix='tmp_config')
    config.set_state_path(path, copy_current=True)
    print('tmp_config state before passing onwards:')
    config.dump()
    old_state = _state_to_dict(config.state)
    yield config
    print('tmp_config state before reverting it:')
    print(diff(old_state, _state_to_dict(config.state)))
    config.set_state_path()
    os.remove(path)


@pytest.fixture
def empty_config():
    fh, path = tempfile.mkstemp(suffix='empty_config')
    config.set_state_path(path)
    yield config
    config.set_state_path()
    os.remove(path)


@pytest.fixture
def live_config():
    config.set_state_path()
    yield config
    config.set_state_path()


@pytest.fixture
def expired_hub_token():
    payload = {
        'email': 'example@example.com',
        'exp': 42,
        'hub_id': 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd',
        'hub_name': 'HubbyMcHubFace',
        'iat': 42,
        'kid': 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd',
        'nickname': 'Demo',
        'owner': True,
        'role': 32,
        'user_id': 'deadbeef-aaaa-bbbb-cccc-tmpusrdddddd',
    }
    yield jwt.encode(payload, 'supersecret').decode('utf-8')


@pytest.fixture
def tmp_cloud(empty_config):
    obj = lambda: 0
    obj.config = empty_config
    obj.section = 'Cloud'
    obj.email = 'example@example.com'
    obj.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.
    obj.expiry = datetime.timedelta(days=1)
    obj.now = datetime.datetime.now()
    obj.iso_now = obj.now.isoformat().split(".")[0]
    obj.yesterday = obj.now - datetime.timedelta(days=1)
    obj.iso_yesterday = obj.yesterday.isoformat().split(".")[0]
    from cozify import cloud
    cloud._setAttr('email', obj.email)
    cloud._setAttr('remotetoken', obj.token)
    cloud._setAttr('last_refresh', obj.iso_yesterday)
    yield obj


@pytest.fixture
def live_cloud(tmp_config):
    from cozify import cloud
    yield cloud


@pytest.fixture
def tmp_hub(tmp_cloud):
    with Tmp_hub(tmp_cloud) as hub_obj:
        yield hub_obj


@pytest.fixture()
def live_hub(tmp_config):
    from cozify import hub
    yield hub


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
    assert dev is not None, 'Cannot run live device tests, no reachable BRIGHTNESS capable device with name including \'test\' to test against.'
    logging.info('online_device state before use ({1}): {0}'.format(store, _h6_dict(store)))
    yield dev
    logging.info('online_device state after use, before rollback ({1}): {0}'.format(
        dev['state'], _h6_dict(dev['state'])))
    hub.device_state_replace(dev['id'], store)


@pytest.fixture()
def live_sensor_temperature():
    dev = None
    devs = hub.devices(capabilities=hub.capability.TEMPERATURE)
    for i, d in devs.items():
        if d['state']['reachable']:
            dev = d
            break
    assert dev is not None, 'Cannot run live sensor tests, no reachable TEMPERATURE capable device to test against.'
    yield dev


@pytest.fixture
def ready_kwargs(live_hub, live_cloud):
    kwargs = {}
    kwargs['hub_id'] = live_hub.default()
    kwargs['hub_token'] = live_hub.token()
    kwargs['cloud_token'] = live_cloud.token()
    kwargs['remote'] = live_hub.remote()
    kwargs['autoremote'] = live_hub.autoremote()
    kwargs['host'] = live_hub.host()
    return kwargs


class Tmp_hub():
    """Creates a temporary hub section (with test data) in a tmp_cloud
    """

    def __init__(self, tmp_cloud):
        self.meta_version = 137
        self.id = 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'
        self.name = 'HubbyMcHubFace'
        self.host = '127.0.0.1'
        self.section = 'Hubs.{0}'.format(self.id)
        self.token = 'eyJkb20iOiJ1ayIsImFsZyI6IkhTNTEyIiwidHlwIjoiSldUIn0.eyJyb2xlIjo4LCJpYXQiOjE1MTI5ODg5NjksImV4cCI6MTUxNTQwODc2OSwidXNlcl9pZCI6ImRlYWRiZWVmLWFhYWEtYmJiYi1jY2NjLWRkZGRkZGRkZGRkZCIsImtpZCI6ImRlYWRiZWVmLWRkZGQtY2NjYy1iYmJiLWFhYWFhYWFhYWFhYSIsImlzcyI6IkNsb3VkIn0.QVKKYyfTJPks_BXeKs23uvslkcGGQnBTKodA-UGjgHg'  # valid but useless jwt token.

    @pytest.mark.usefixtures("tmp_cloud")
    def __enter__(self):
        config.state.add_section('meta')
        config.state['meta']['version'] = str(self.meta_version)
        config.state.add_section(self.section)
        config.state[self.section]['hubname'] = self.name
        config.state[self.section]['host'] = self.host
        config.state[self.section]['hubtoken'] = self.token
        config.state['Hubs']['default'] = self.id
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        config.set_state_path()

    def devices(self):
        return dev.device_ids, dev.devices

    def states(self):
        return dev.states


def _h6_dict(d):
    j = json.dumps(d)
    w = j.encode('utf8')
    h = hashlib.md5(w)
    return h.hexdigest()[:6]


def _state_to_dict(state):
    out = dict(state)
    for section in out:
        out[section] = dict(out[section])
    return out
