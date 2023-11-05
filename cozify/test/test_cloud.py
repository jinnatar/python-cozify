#!/usr/bin/env python3

import datetime
import os
import tempfile
import time

import pytest

from cozify import cloud, config, hub
from cozify.Error import AuthenticationError
from cozify.test import debug
from cozify.test.fixtures import *

## basic cloud.authenticate() tests


@pytest.mark.live
def test_cloud_authenticate(live_cloud):
    assert live_cloud.authenticate()
    live_cloud.resetState()
    with pytest.raises(OSError):
        # Raises an OSError because trying to read email address interactively
        live_cloud.authenticate()
    assert live_cloud._need_cloud_token()


@pytest.mark.logic
def test_cloud_ping_cold(blank_cloud):
    with pytest.raises(OSError):
        # Raises an OSError because trying to read email address interactively
        blank_cloud.ping()


@pytest.mark.live
def test_cloud_authenticate_hub(live_cloud):
    assert live_cloud.authenticate(trustHub=False)


@pytest.mark.logic
def test_cloud_noninteractive_otp():
    with pytest.raises(AuthenticationError) as e_info:
        cloud._getotp()


## Misc feature logic tests


@pytest.mark.logic
def test_cloud_token_set_reset(blank_cloud):
    blank_cloud.token("foobar")
    assert blank_cloud.token() == "foobar"
    blank_cloud.resetState()
    with pytest.raises(AttributeError) as e_info:
        blank_cloud._getAttr("remotetoken")


## cloud.refresh() logic tests


@pytest.mark.logic
def test_cloud_refresh_cold(tmp_cloud):
    config.state.remove_option("Cloud", "last_refresh")
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=tmp_cloud.expiry)


@pytest.mark.logic
def test_cloud_refresh_force(tmp_cloud):
    config.dump_state()
    assert cloud._need_refresh(force=True, expiry=datetime.timedelta(days=365))


@pytest.mark.logic
def test_cloud_refresh_invalid(tmp_cloud):
    config.state["Cloud"]["last_refresh"] = "intentionally bad"
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(days=365))


@pytest.mark.logic
def test_cloud_refresh_expiry_over(tmp_cloud):
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(hours=1))


@pytest.mark.logic
def test_cloud_refresh_expiry_not_over(tmp_cloud):
    config.dump_state()
    assert not cloud._need_refresh(force=False, expiry=datetime.timedelta(days=2))


@pytest.mark.destructive
def test_cloud_refresh_force(live_cloud):
    config.dump_state()
    timestamp_before = live_cloud._getAttr("last_refresh")
    token_before = live_cloud.token()
    time.sleep(2)  # ensure timestamp has a diff
    live_cloud.refresh(force=True)
    config.dump_state()
    assert timestamp_before < live_cloud._getAttr("last_refresh")
    assert token_before != live_cloud.token()


## integration tests for remote


@pytest.mark.live
def test_cloud_remote_match(live_cloud, live_hub):
    config.dump_state()
    live_hub.ping()
    local_tz = live_hub.tz()
    remote_tz = live_hub.tz(remote=True)

    assert local_tz == remote_tz
