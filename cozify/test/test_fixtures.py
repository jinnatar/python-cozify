#!/usr/bin/env python3
import pytest

from cozify import config
from cozify.test import debug
from cozify.test.fixtures import *
from cozify.Error import APIError


@pytest.fixture(autouse=True)
def run_around_tests():
    print('Before fixture:')
    config.dump()
    assert 'default' in config.state['Hubs'] and 'email' in config.state['Cloud'], 'State failed before fixture.'
    prev_default = config.state['Hubs']['default']
    prev_email = config.state['Cloud']['email']
    prev_remote = config.state['Hubs.' + config.state['Hubs']['default']]['remote']
    yield
    print('After fixture:')
    config.dump()
    assert 'default' in config.state['Hubs'] and 'email' in config.state['Cloud'], 'State failed due to fixture.'
    assert prev_default == config.state['Hubs']['default']
    assert prev_email == config.state['Cloud']['email']
    assert prev_remote == config.state['Hubs.' + config.state['Hubs']['default']]['remote']


@pytest.mark.logic
def test_fixture_tmp_hub(tmp_hub):
    assert config.state['Cloud']['email'] == 'example@example.com'
    assert config.state['Hubs']['default'] == 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'


@pytest.mark.live
def test_fixture_live_hub(live_hub):
    hub = config.state['Hubs']['default']
    assert hub != 'deadbeef-aaaa-bbbb-cccc-tmphubdddddd'
    assert live_hub.ping()


@pytest.mark.logic
def test_fixture_tmp_cloud(tmp_cloud):
    email = config.state['Cloud']['email']
    assert email == 'example@example.com'


@pytest.mark.live
def test_fixture_live_cloud(live_cloud):
    email = config.state['Cloud']['email']
    assert email != 'example@example.com'
    assert live_cloud.ping()
