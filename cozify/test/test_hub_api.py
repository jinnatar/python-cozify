#!/usr/bin/env python3
import pytest
from mbtest.imposters import Imposter, Predicate, Response, Stub

from cozify import cloud, config, hub, hub_api
from cozify.Error import APIError, AuthenticationError, ConnectionError
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
        hub_token=live_hub.token(hub_id),
    )


@pytest.mark.mbtest
def test_hub_api_timeout(mock_server, tmp_hub):
    imposter = Imposter(
        Stub(Predicate(path="/hub/tz"), Response(body="Europe/Helsinki", wait=6000))
    )
    with pytest.raises(ConnectionError) as e_info:
        with mock_server(imposter):
            hub_api.tz(
                host=imposter.host, port=imposter.port, base="", hub_token=tmp_hub.token
            )
