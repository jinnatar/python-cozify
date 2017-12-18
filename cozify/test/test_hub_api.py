#!/usr/bin/env python3
import pytest

from cozify import conftest
from cozify import cloud, hub, hub_api, config

tmphub = lambda:0
tmpcloud = lambda:0

@pytest.fixture
def default_hub(scope='module'):
    tmphub.hub_id = hub.getDefaultHub()
    tmphub.name = hub.name(tmphub.hub_id)
    tmphub.host = hub.host(tmphub.hub_id)
    tmphub.token = hub.token(tmphub.hub_id)
    return tmphub

@pytest.fixture
def live_cloud(scope='module'):
    tmpcloud.token = cloud.token()
    return tmpcloud


@pytest.mark.live
def test_hub(live_cloud, default_hub):
    assert hub_api.hub(
            host = default_hub.host,
            remoteToken = live_cloud.token,
            hubToken = default_hub.token
            )
