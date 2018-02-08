#!/usr/bin/env python3
import pytest

from cozify import conftest
from cozify import cloud, hub, hub_api, config

@pytest.mark.live
def test_hub(live_cloud, default_hub):
    assert hub_api.hub(
            host = default_hub.host,
            remote = default_hub.remote,
            remote_token = live_cloud.token(),
            hub_token = default_hub.token
            )
