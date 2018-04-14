#!/usr/bin/env python3
import pytest

from cozify import hub, multisensor
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import APIError


@pytest.mark.logic
def test_hub_tmp_hub(tmp_hub):
    assert config.state['Cloud']['email'] == 'example@example.com'
    assert config.state['Hubs']['default'] == 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'


@pytest.mark.live
def test_hub_tz(live_hub):
    assert hub.ping()
    assert hub.tz()


@pytest.mark.live
def test_hub_remote_naive(live_hub):
    assert hub.tz()


@pytest.mark.logic
def test_hub_remote_set(tmp_hub):
    assert hub.remote(tmp_hub.id, True) == True
    assert hub.remote(tmp_hub.id) == True
    assert hub.remote(tmp_hub.id, False) == False
    assert hub.remote(tmp_hub.id) == False


@pytest.mark.logic
def test_hub_autoremote_set(tmp_hub):
    assert hub.autoremote(tmp_hub.id, True) == True
    assert hub.autoremote(tmp_hub.id) == True
    assert hub.autoremote(tmp_hub.id, False) == False
    assert hub.autoremote(tmp_hub.id) == False


@pytest.mark.logic
def test_hub_id_to_name(tmp_hub):
    assert hub.name(tmp_hub.id) == tmp_hub.name


@pytest.mark.logic
def test_hub_name_to_id(tmp_hub):
    assert hub.hub_id(tmp_hub.name) == tmp_hub.id


@pytest.mark.live
def test_multisensor(live_hub):
    assert hub.ping()
    data = hub.devices()
    print(multisensor.getMultisensorData(data))


@pytest.mark.logic
def test_hub_get_id(tmp_hub):
    assert hub._get_id(hub_id=tmp_hub.id) == tmp_hub.id
    assert hub._get_id(hub_name=tmp_hub.name) == tmp_hub.id
    assert hub._get_id(hub_name=tmp_hub.name, hub_id=tmp_hub.id) == tmp_hub.id
    assert hub._get_id(hubName=tmp_hub.name) == tmp_hub.id
    assert hub._get_id(hubId=tmp_hub.id) == tmp_hub.id
    assert hub._get_id() == tmp_hub.id
    assert not hub._get_id(hub_id='foo') == tmp_hub.id


@pytest.mark.destructive
def test_hub_ping_autorefresh(live_hub):
    assert hub.ping()
    hub_id = live_hub.default()
    live_hub.token(hub_id=hub_id, new_token='destroyed-on-purpose-by-destructive-test')

    assert not live_hub.ping(autorefresh=False)
    with pytest.raises(APIError):
        hub.tz()
    assert live_hub.ping(autorefresh=True)


@pytest.mark.live
def test_hub_fill_kwargs(live_hub):
    assert hub.ping()
    kwargs = {}
    hub._fill_kwargs(kwargs)
    for key in ['hub_id', 'remote', 'autoremote', 'hub_token', 'cloud_token', 'host']:
        assert key in kwargs, 'key {0} did not get set.'.format(key)
        if key != 'host' or (key == 'host' and not live_hub.remote(hub.default())):
            assert kwargs[key] is not None, 'key {0} was set to None'.format(key)


@pytest.mark.logic
def test_hub_clean_state(tmp_hub):
    states = tmp_hub.states()
    assert states['clean'] == hub._clean_state(states['dirty'])


@pytest.mark.logic
def test_hub_in_range():
    assert hub._in_range(0.5, low=0.0, high=1.0)
    assert hub._in_range(0.0, low=0.0, high=1.0)
    assert hub._in_range(1.0, low=0.0, high=1.0)
    assert hub._in_range(None, low=0.0, high=1.0)
    with pytest.raises(ValueError):
        hub._in_range(1.5, low=0.0, high=1.0)
    with pytest.raises(ValueError):
        hub._in_range(-0.5, low=0.0, high=1.0)


@pytest.mark.destructive
@pytest.mark.remote
def test_hub_dirty_remote(live_hub):
    # test if we are remote to get meaningful results
    live_hub.ping(live_hub.default())
    if not live_hub.remote(live_hub.default()):
        pytest.xfail("Not remote, cannot run this test")
    else:
        # fuck up the state on purpose to say we're not remote
        assert not live_hub.remote(live_hub.default(), False)
        # attempt to repair the state
        assert live_hub.ping()
        # verify we're now considered to be remote
        assert live_hub.remote(live_hub.default())
