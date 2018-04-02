#!/usr/bin/env python3
import pytest

from cozify import hub, hub_api, config, multisensor
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import APIError


@pytest.mark.live
def test_hub_tz(live_hub):
    assert hub.ping()
    assert hub.tz()


@pytest.mark.live
def test_hub_remote_naive(live_hub):
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
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram']])
    assert len(out) == 2


def test_hub_devices_filter_or(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=False,
        capabilities=[hub.capability.TWILIGHT, hub.capability.COLOR_HS],
        mock_devices=devs)
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram'], ids['twilight_nexa']])
    assert len(out) == 3


def test_hub_devices_filter_and(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=True,
        capabilities=[hub.capability.COLOR_HS, hub.capability.COLOR_TEMP],
        mock_devices=devs)
    assert all(i in out for i in [ids['lamp_osram'], ids['strip_osram']])
    assert len(out) == 2


@pytest.mark.destructive
def test_hub_ping_autorefresh(live_hub):
    hub_id = live_hub.default()
    live_hub.token(hub_id=hub_id, new_token='destroyed-on-purpose-by-destructive-test')

    assert not live_hub.ping(autorefresh=False)
    with pytest.raises(APIError):
        hub.tz()
    assert live_hub.ping(autorefresh=True)


def test_hub_device_eligible(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_eligible(ids['lamp_osram'], hub.capability.COLOR_TEMP, mock_devices=devs)
    assert not hub.device_eligible(
        ids['twilight_nexa'], hub.capability.COLOR_TEMP, mock_devices=devs)


def test_hub_device_implicit_state(tmp_hub):
    ids, devs = tmp_hub.devices()
    state = {}
    hub.device_eligible(
        ids['lamp_osram'], hub.capability.COLOR_TEMP, mock_devices=devs, state=state)
    assert 'temperature' in state
    hub.device_exists(ids['twilight_nexa'], mock_devices=devs, state=state)
    assert 'twilight' in state


def test_hub_device_reachable(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_reachable(ids['reachable'], mock_devices=devs)
    assert not hub.device_reachable(ids['not-reachable'], mock_devices=devs)
    with pytest.raises(ValueError):
        hub.device_reachable('dead-beef', mock_devices=devs)


def test_hub_device_exists(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_exists(ids['reachable'], mock_devices=devs)
    assert not hub.device_exists('dead-beef', mock_devices=devs)
