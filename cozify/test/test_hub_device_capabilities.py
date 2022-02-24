#!/usr/bin/env python3
import pytest, time

from absl import logging

from cozify import hub
from cozify.test import debug
from cozify.test.fixtures import live_hub, online_device, real_test_devices
from cozify.Error import APIError

# global timer delay for tests that change device state
delay = 5


@pytest.mark.destructive
@pytest.mark.vcr
def test_hub_device_capability_color_temp(live_hub, real_test_devices):
    cap = 'COLOR_TEMP'
    if cap not in real_test_devices:
        pytest.xfail(f'Cannot test capability, no designated test device that has capability {cap}')
    i = real_test_devices[cap]
    dev = live_hub.devices(capabilities=hub.capability[cap])[i]

    old_value = dev['state']['temperature']
    if old_value - 100 >= dev['state']['minTemperature']:
        set_value = old_value - 100
    elif old_value + 100 <= dev['state']['maxTemperature']:
        set_value = old_value + 100
    live_hub.light_temperature(i, temperature=set_value)

    time.sleep(delay)
    dev = live_hub.devices(capabilities=hub.capability[cap])[i]
    new_value = dev['state']['temperature']
    logging.info(f'Expecting {old_value} -> {set_value}, got: {new_value}')
    assert new_value == set_value
