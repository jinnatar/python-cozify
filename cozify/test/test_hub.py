#!/usr/bin/env python3
import pytest

from cozify import conftest

from cozify import hub, hub_api, config, multisensor
from cozify.test import debug

class tmp_hub():
    """Creates a temporary hub section (with test data) in the current live state.
    """
    def __init__(self):
        self.id = 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'
        self.name = 'HubbyMcHubFace'
        self.host = '127.0.0.1'
        self.section = 'Hubs.{0}'.format(self.id)
    def __enter__(self):
        config.setStatePath() # reset to default
        config.state.add_section(self.section)
        config.state[self.section]['hubname'] = self.name
        config.state[self.section]['host'] = self.host
        config.state['Hubs']['default'] = self.id
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            debug.logger.error("%s, %s, %s" % (exc_type, exc_value, traceback))
            return False
        config.state.remove_section(self.section)

@pytest.fixture
def tmphub(scope='module'):
    with tmp_hub() as hub:
        yield hub

@pytest.fixture
def id(scope='module'):
    return 'deadbeef-aaaa-bbbb-cccc-dddddddddddd'

@pytest.fixture
def livehub(scope='module'):
    config.setStatePath() # default config assumed to be live
    config.dump_state() # dump state so it's visible in failed test output
    assert hub.ping()
    return hub

@pytest.mark.live
def test_tz(livehub):
    assert hub.tz()

    # hand craft data needed for low-level api call hub_api.tz
    hubSection = 'Hubs.' + config.state['Hubs']['default']
    print(hub_api.tz(
        host=config.state[hubSection]['host'],
        hub_token=config.state[hubSection]['hubtoken'],
        remote=hub.remote,
        cloud_token=config.state['Cloud']['remotetoken']
        ))

def test_hub_id_to_name(tmphub):
    assert hub.name(tmphub.id) == tmphub.name

def test_hub_name_to_id(tmphub):
    assert hub.getHubId(tmphub.name) == tmphub.id

@pytest.mark.live
def test_multisensor(livehub):
    data = hub.getDevices()
    print(multisensor.getMultisensorData(data))

def test_hub_get_id(tmphub):
    assert hub._get_id(hub_id=tmphub.id) == tmphub.id
    assert hub._get_id(hub_name=tmphub.name) == tmphub.id
    assert hub._get_id(hub_name=tmphub.name, hub_id=tmphub.id) == tmphub.id
    assert hub._get_id(hubName=tmphub.name) == tmphub.id
    assert hub._get_id(hubId=tmphub.id) == tmphub.id
    assert hub._get_id() == tmphub.id
    assert not hub._get_id(hub_id='foo') == tmphub.id

