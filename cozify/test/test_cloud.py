#!/usr/bin/env python3

import os, pytest, tempfile, datetime

from cozify import cloud
from cozify.test import debug, state_verify
from cozify.test.fixtures import tmp_config, empty_config, tmp_cloud, live_cloud
from cozify.Error import AuthenticationError

## basic cloud.authenticate() tests


@pytest.mark.live
def test_cloud_authenticate(tmp_config):
    assert cloud.authenticate()
    assert False


@pytest.mark.live
def test_cloud_authenticate_hub(tmp_config):
    assert cloud.authenticate(trustHub=False)
    assert False


@pytest.mark.logic
def test_cloud_noninteractive_otp():
    with pytest.raises(AuthenticationError) as e_info:
        cloud._getotp()


## cloud.refresh() logic tests


@pytest.mark.logic
def test_cloud_refresh_cold(tmp_cloud):
    tmp_cloud.config.state.remove_option('Cloud', 'last_refresh')
    tmp_cloud.config.dump()
    assert cloud._need_refresh(force=False, expiry=tmp_cloud.expiry)


@pytest.mark.logic
def test_cloud_refresh_force(tmp_cloud):
    tmp_cloud.config.dump()
    assert cloud._need_refresh(force=True, expiry=datetime.timedelta(days=365))


@pytest.mark.logic
def test_cloud_refresh_invalid(tmp_cloud):
    tmp_cloud.config.state['Cloud']['last_refresh'] = 'intentionally bad'
    tmp_cloud.config.dump()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(days=365))


@pytest.mark.logic
def test_cloud_refresh_expiry_over(tmp_cloud):
    tmp_cloud.config.dump()
    assert cloud._need_refresh(force=False, expiry=datetime.timedelta(hours=1))


@pytest.mark.logic
def test_cloud_refresh_expiry_not_over(tmp_cloud):
    tmp_cloud.config.dump()
    assert not cloud._need_refresh(force=False, expiry=datetime.timedelta(days=2))
