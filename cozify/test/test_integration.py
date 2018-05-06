#!/usr/bin/env python3
import pytest

from cozify import hub, cloud
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import APIError


@pytest.mark.destructive
def test_integration_ping_autorenew(live_hub, live_cloud):
    # make sure state is as expected before mangling it
    assert live_hub.ping()
    assert live_cloud.ping()

    # trash the hub_token
    hub_id = live_hub.default()
    live_hub.token(hub_id=hub_id, new_token='destroyed-on-purpose-by-destructive-integration-test')
    assert not live_hub.ping(autorefresh=False)
    with pytest.raises(APIError):
        hub.tz()
    assert live_hub.ping(autorefresh=True)

    ancient_date = '2000-01-01T00:00:00'
    live_cloud._setAttr('last_refresh', ancient_date, commit=False)
    assert live_hub.ping(autorefresh=True)
    assert live_cloud._getAttr('last_refresh') != ancient_date, 'cloud was not autorefreshed'


@pytest.mark.live
def test_integration_remote_match(live_cloud, live_hub):
    config.dump_state()
    live_hub.ping()
    local_tz = live_hub.tz()
    remote_tz = live_hub.tz(remote=True)

    assert local_tz == remote_tz
