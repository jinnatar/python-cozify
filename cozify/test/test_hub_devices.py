#!/usr/bin/env python3
import pytest, time

from cozify import hub
from cozify.test import debug
from cozify.test.fixtures import live_hub, tmp_hub, tmp_cloud, online_device
from cozify.Error import APIError

# global timer delay for tests that change device state
delay = 2


@pytest.mark.logic
def test_hub_devices_filter_single(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(hub_id=tmp_hub.id, capabilities=hub.capability.COLOR_LOOP, mock_devices=devs)
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram']])
    assert len(out) == 2


@pytest.mark.logic
def test_hub_devices_filter_or(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=False,
        capabilities=[hub.capability.TWILIGHT, hub.capability.COLOR_HS],
        mock_devices=devs)
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram'], ids['twilight_nexa']])
    assert len(out) == 3


@pytest.mark.logic
def test_hub_devices_filter_and(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=True,
        capabilities=[hub.capability.COLOR_HS, hub.capability.COLOR_TEMP],
        mock_devices=devs)
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram']])
    assert len(out) == 2


@pytest.mark.logic
def test_hub_device_eligible(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_eligible(ids['lamp_osram'], hub.capability.COLOR_TEMP, mock_devices=devs)
    assert not hub.device_eligible(
        ids['twilight_nexa'], hub.capability.COLOR_TEMP, mock_devices=devs)


@pytest.mark.logic
def test_hub_device_implicit_state(tmp_hub):
    ids, devs = tmp_hub.devices()
    state = {}
    hub.device_eligible(
        ids['lamp_osram'], hub.capability.COLOR_TEMP, mock_devices=devs, state=state)
    assert 'temperature' in state
    hub.device_exists(ids['twilight_nexa'], mock_devices=devs, state=state)
    assert 'twilight' in state


@pytest.mark.logic
def test_hub_device_reachable(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_reachable(ids['reachable'], mock_devices=devs)
    assert not hub.device_reachable(ids['not-reachable'], mock_devices=devs)
    with pytest.raises(ValueError):
        hub.device_reachable('dead-beef', mock_devices=devs)


@pytest.mark.logic
def test_hub_device_exists(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_exists(ids['reachable'], mock_devices=devs)
    assert not hub.device_exists('dead-beef', mock_devices=devs)


@pytest.mark.destructive
@pytest.mark.vcr
def test_hub_device_toggle(live_hub, online_device):
    live_hub.device_toggle(online_device['id'])
    time.sleep(delay)


@pytest.mark.destructive
def test_hub_device_on_off(live_hub, online_device):
    if online_device['state']['isOn']:
        live_hub.device_off(online_device['id'])
        time.sleep(delay)
        live_hub.device_on(online_device['id'])
    else:
        live_hub.device_on(online_device['id'])
    time.sleep(delay)


@pytest.mark.destructive
def test_hub_device_state_replace(live_hub, online_device):
    live_hub.device_on(online_device['id'])

    old_brightness = online_device['state']['brightness']
    if old_brightness > 0.1:
        set_brightness = old_brightness - 0.1
    else:
        set_brightness = 0.5
    online_device['state']['brightness'] = set_brightness
    online_device['state']['isOn'] = True
    live_hub.device_state_replace(online_device['id'], online_device['state'])
    time.sleep(delay)
    devs = live_hub.devices()
    new_brightness = devs[online_device['id']]['state']['brightness']
    new_isOn = devs[online_device['id']]['state']['isOn']

    assert new_brightness != old_brightness, 'brightness did not change, expected {0}'.format(new_brightness)
    assert new_brightness == set_brightness, 'brightness changed unexpectedly, expected {0}'.format(set_brightness)
    assert new_isOn == True
