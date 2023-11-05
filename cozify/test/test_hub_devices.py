#!/usr/bin/env python3
import time
from math import isclose

import pytest

from cozify import hub
from cozify.Error import APIError
from cozify.test import debug
from cozify.test.fixtures import (
    live_hub,
    online_device,
    real_test_devices,
    tmp_cloud,
    tmp_hub,
)

# global timer delay for tests that change device state
delay = 2


@pytest.mark.logic
def test_hub_devices_filter_single(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id, capabilities=hub.capability.COLOR_LOOP, mock_devices=devs
    )
    assert all(i in out for i in [ids["lamp_osram"], ids["strip_osram"]])
    assert len(out) == 2


@pytest.mark.logic
def test_hub_devices_filter_or(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=False,
        capabilities=[hub.capability.TWILIGHT, hub.capability.COLOR_HS],
        mock_devices=devs,
    )
    assert all(
        i in out for i in [ids["lamp_osram"], ids["strip_osram"], ids["twilight_nexa"]]
    )
    assert len(out) == 3


@pytest.mark.logic
def test_hub_devices_filter_and(tmp_hub):
    ids, devs = tmp_hub.devices()
    out = hub.devices(
        hub_id=tmp_hub.id,
        and_filter=True,
        capabilities=[hub.capability.COLOR_HS, hub.capability.COLOR_TEMP],
        mock_devices=devs,
    )
    assert all(i in out for i in [ids["lamp_osram"], ids["strip_osram"]])
    assert len(out) == 2


@pytest.mark.logic
def test_hub_device_eligible(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_eligible(
        ids["lamp_osram"], hub.capability.COLOR_TEMP, mock_devices=devs
    )
    assert not hub.device_eligible(
        ids["twilight_nexa"], hub.capability.COLOR_TEMP, mock_devices=devs
    )


@pytest.mark.logic
def test_hub_device_implicit_state(tmp_hub):
    ids, devs = tmp_hub.devices()
    state = {}
    hub.device_eligible(
        ids["lamp_osram"], hub.capability.COLOR_TEMP, mock_devices=devs, state=state
    )
    assert "temperature" in state
    hub.device_exists(ids["twilight_nexa"], mock_devices=devs, state=state)
    assert "twilight" in state


@pytest.mark.logic
def test_hub_device_reachable(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_reachable(ids["reachable"], mock_devices=devs)
    assert not hub.device_reachable(ids["not-reachable"], mock_devices=devs)
    with pytest.raises(ValueError):
        hub.device_reachable("dead-beef", mock_devices=devs)


@pytest.mark.logic
def test_hub_device_exists(tmp_hub):
    ids, devs = tmp_hub.devices()
    assert hub.device_exists(ids["reachable"], mock_devices=devs)
    assert not hub.device_exists("dead-beef", mock_devices=devs)


@pytest.mark.destructive
@pytest.mark.vcr
def test_hub_device_toggle(live_hub, online_device):
    live_hub.device_toggle(online_device["id"])
    time.sleep(delay)


@pytest.mark.destructive
def test_hub_device_on_off(live_hub, online_device):
    with pytest.raises(ValueError):
        live_hub.device_on("dead-beef")
    with pytest.raises(ValueError):
        live_hub.device_off("dead-beef")
    if online_device["state"]["isOn"]:
        live_hub.device_off(online_device["id"])
        time.sleep(delay)
        live_hub.device_on(online_device["id"])
    else:
        live_hub.device_on(online_device["id"])
        time.sleep(delay)
        live_hub.device_off(online_device["id"])
    time.sleep(delay)


@pytest.mark.destructive
def test_hub_device_state_replace(live_hub, real_test_devices):
    if "BRIGHTNESS" not in real_test_devices:
        pytest.xfail("No test device available with brightness control")
    dev_id = real_test_devices["BRIGHTNESS"]
    dev = live_hub.device(dev_id)

    live_hub.device_on(dev_id)
    old_brightness = dev["state"]["brightness"]
    if old_brightness > 0.1:
        set_brightness = old_brightness - 0.1
    else:
        set_brightness = 0.5
    dev["state"]["brightness"] = set_brightness
    dev["state"]["isOn"] = True
    live_hub.device_state_replace(dev_id, dev["state"])

    time.sleep(delay)

    dev = live_hub.device(dev_id)
    new_brightness = dev["state"]["brightness"]
    new_isOn = dev["state"]["isOn"]

    # We allow 1% deviance due to device specific snafus
    assert isclose(
        new_brightness, set_brightness, rel_tol=0.01
    ), f"brightness is wrong, expected {set_brightness} but got {new_brightness}"
    assert new_isOn == True
