#!/usr/bin/env python3
import pytest

from cozify import conftest

from cozify import hub, hub_api, config, multisensor
from cozify.test import debug

@pytest.mark.live
def test_tz(live_hub):
    assert hub.ping()
    assert hub.tz()

@pytest.mark.live
def test_remote_naive(live_hub):
    assert hub.tz()

def test_hub_id_to_name(tmp_hub):
    assert hub.name(tmp_hub.id) == tmp_hub.name

def test_hub_name_to_id(tmp_hub):
    assert hub.hub_id(tmp_hub.name) == tmp_hub.id

@pytest.mark.live
def test_multisensor(live_hub):
    assert hub.ping()
    data = hub.devices()
    print(multisensor.getMultisensorData(data))

def test_hub_get_id(tmp_hub):
    assert hub._get_id(hub_id=tmp_hub.id) == tmp_hub.id
    assert hub._get_id(hub_name=tmp_hub.name) == tmp_hub.id
    assert hub._get_id(hub_name=tmp_hub.name, hub_id=tmp_hub.id) == tmp_hub.id
    assert hub._get_id(hubName=tmp_hub.name) == tmp_hub.id
    assert hub._get_id(hubId=tmp_hub.id) == tmp_hub.id
    assert hub._get_id() == tmp_hub.id
    assert not hub._get_id(hub_id='foo') == tmp_hub.id

def test_hub_devices_filter_single(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(hub_id=tmp_hub.id, capabilities=hub.capability.COLOR_LOOP, mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'] ])
    assert len(out) == 2

def test_hub_devices_filter_or(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(hub_id=tmp_hub.id, and_filter=False, capabilities=[hub.capability.TWILIGHT, hub.capability.COLOR_HS], mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'], ids['twilight_nexa'] ])
    assert len(out) == 3

def test_hub_devices_filter_and(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(hub_id=tmp_hub.id, and_filter=True, capabilities=[hub.capability.COLOR_HS, hub.capability.COLOR_TEMP], mock_devices=devs)
    assert all(i in out for i in [ ids['lamp_osram'], ids['strip_osram'] ])
    assert len(out) == 2

@pytest.mark.destructive
def test_hub_ping_autorefresh(live_hub):
    hub_id = live_hub.default()
    live_hub.token(hub_id=hub_id, new_token='destroyed-on-purpose-by-destructive-test')
    assert not live_hub.ping(autorefresh=False)
    assert live_hub.ping(autorefresh=True)
