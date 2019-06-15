#!/usr/bin/env python3
import pytest, os

from cozify import hub, cloud
from cozify.test import debug, state_verify
from cozify.test.fixtures import *
from cozify.Error import APIError


@pytest.mark.destructive
def test_integration_ping_autorefresh(live_hub, live_cloud, expired_hub_token):
    # make sure state is as expected before mangling it
    assert live_hub.ping()
    assert live_cloud.ping()

    # trash the hub_token
    hub_id = live_hub.default()
    live_hub.token(hub_id=hub_id, new_token=expired_hub_token)
    assert not live_hub.ping(autorefresh=False)
    with pytest.raises(APIError):
        hub.tz()
    assert live_hub.ping(autorefresh=True)

    live_hub.token(hub_id=hub_id, new_token=expired_hub_token)
    ancient_date = '2000-01-01T00:00:00'
    live_cloud._setAttr('last_refresh', ancient_date, commit=False)
    assert live_hub.ping(autorefresh=True)
    assert live_cloud._getAttr('last_refresh') != ancient_date, 'cloud was not autorefreshed'


@pytest.mark.live
def test_integration_remote_match(live_cloud, live_hub):
    config.dump()
    live_hub.ping()
    local_tz = live_hub.tz()
    remote_tz = live_hub.tz(remote=True)

    assert local_tz == remote_tz


@pytest.mark.logic
def test_travis_debug():
    if 'TRAVIS' not in os.environ:
        pytest.xfail('This test can only succeed in a Travis environment.')

    oldval = os.environ["TRAVIS"]
    os.environ["TRAVIS"] = "true"
    from cozify import http
    assert http.session.trust_env == False

    os.environ["TRAVIS"] = oldval


@pytest.mark.live
def test_proxy():
    if 'Proxies' not in config.state:
        pytest.xfail('This test can only succeed if the Proxies section is defined in the config.')

    import requests
    import logging
    import http.client as http_client
    http_client.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    proxies = dict(config.state['Proxies'])
    s = requests.Session()
    s.proxies = proxies
    s.timeout = 5
    r = s.get('https://example.com')
    assert r.status_code == 200
