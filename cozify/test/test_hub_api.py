#!/usr/bin/env python3
import pytest

from cozify import conftest
from cozify import cloud, hub, hub_api, config

tmphub = lambda:0
tmpcloud = lambda:0

@pytest.fixture
def default_hub(scope='module'):
    config.setStatePath() # reset to default config
    config.dump_state()
    tmphub.hub_id = hub.getDefaultHub()
    tmphub.name = hub.name(tmphub.hub_id)
    tmphub.host = hub.host(tmphub.hub_id)
    tmphub.token = hub.token(tmphub.hub_id)
    tmphub.remote = hub.remote
    return tmphub

@pytest.fixture
def live_cloud(scope='module'):
    tmpcloud.token = cloud.token()
    return tmpcloud


@pytest.mark.live
def test_hub(live_cloud, default_hub):
    assert hub_api.hub(
            host = default_hub.host,
            remote = default_hub.remote,
            remote_token = live_cloud.token,
            hub_token = default_hub.token
            )
