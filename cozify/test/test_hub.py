#!/usr/bin/env python3
import pytest

from cozify import conftest

from cozify import hub, hub_api, config, multisensor
from cozify.test import debug

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

def test_hub_devices_filter_single(tmphub):
    ids, devs = tmphub.devices()
    out = hub.devices(hub_id=tmphub.id, capabilities=hub.capability.COLOR_LOOP, mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'] ])
    assert len(out) == 2

def test_hub_devices_filter_or(tmphub):
    ids, devs = tmphub.devices()
    out = hub.devices(hub_id=tmphub.id, and_filter=False, capabilities=[hub.capability.TWILIGHT, hub.capability.COLOR_HS], mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'], ids['twilight_nexa'] ])
    assert len(out) == 3

def test_hub_devices_filter_and(tmphub):
    ids, devs = tmphub.devices()
    out = hub.devices(hub_id=tmphub.id, and_filter=True, capabilities=[hub.capability.COLOR_HS, hub.capability.COLOR_TEMP], mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'] ])
    assert len(out) == 2
