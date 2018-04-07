#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from cozify import cloud, config, hub
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import AuthenticationError

## basic cloud.authenticate() tests


@pytest.mark.live
def test_cloud_authenticate():
    assert cloud.authenticate()


@pytest.mark.live
def test_cloud_authenticate_hub():
    assert cloud.authenticate(trustHub=False)


@pytest.mark.logic
def test_cloud_noninteractive_otp():
    with pytest.raises(AuthenticationError) as e_info:
        cloud._getotp()


## cloud.refresh() logic tests


@pytest.mark.logic
def test_cloud_refresh_cold(tmp_cloud):
    config.state.remove_option('Cloud', 'last_refresh')
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=tmp_cloud.expiry)


@pytest.mark.logic
def test_cloud_refresh_force(tmp_cloud):
    config.dump_state()
    assert cloud._need_refresh(force=True, expiry=datetime.timedelta(days=365))


@pytest.mark.logic
def test_cloud_refresh_invalid(tmp_cloud):
    config.state['Cloud']['last_refresh'] = 'intentionally bad'
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


## integration tests for remote


@pytest.mark.live
def test_cloud_remote_match(live_cloud, live_hub):
    config.dump_state()
    live_hub.ping()
    local_tz = live_hub.tz()
    remote_tz = live_hub.tz(remote=True)

    assert local_tz == remote_tz
