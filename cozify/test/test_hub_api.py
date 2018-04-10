#!/usr/bin/env python3
import pytest

from cozify import cloud, hub, hub_api, config
from cozify.test import debug
from cozify.test.fixtures import *


@pytest.mark.live
def test_hub(live_cloud, live_hub):
    assert live_hub.ping()
    hub_id = live_hub.default()
    assert hub_api.hub(
        hub_id=hub_id,
        host=live_hub.host(hub_id),
        remote=live_hub.remote(hub_id),
        cloud_token=live_cloud.token(),
        hub_token=live_hub.token(hub_id))
