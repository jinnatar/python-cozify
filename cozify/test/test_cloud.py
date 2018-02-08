#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from cozify import conftest

from cozify import cloud, config, hub
from cozify.test import debug

## basic cloud.authenticate() tests

@pytest.mark.live
def test_auth_cloud():
    assert cloud.authenticate()

@pytest.mark.live
def test_auth_hub():
    assert cloud.authenticate(trustHub=False)

## cloud.refresh() logic tests

def test_cloud_refresh_cold(tmp_cloud):
    config.state.remove_option('Cloud', 'last_refresh')
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=tmp_cloud.expiry)

def test_cloud_refresh_force(tmp_cloud):
    config.dump_state()
    assert cloud._need_refresh(force=True, expiry=datetime.timedelta(days=365))

def test_cloud_refresh_expiry_over(tmp_cloud):
    config.dump_state()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(hours=1))

def test_cloud_refresh_expiry_not_over(tmp_cloud):
    config.dump_state()
    assert not cloud._need_refresh(force=False, expiry=datetime.timedelta(days=2))

## integration tests for remote

@pytest.mark.live
def test_cloud_remote_match(live_cloud):
    config.dump_state()
    local_tz = hub.tz()
    remote_tz = hub.tz(remote=True)

    assert local_tz == remote_tz
