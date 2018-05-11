#!/usr/bin/env python3
import pytest

from cozify import config
from cozify.test import debug


@pytest.fixture(autouse=True)
def run_around_tests():
    prev_path = config.state_path
    print('State before test ({0}):'.format(prev_path))
    config.dump()
    assert 'default' in config.state['Hubs'] and 'email' in config.state['Cloud'], 'State failed before fixture.'
    prev_default = config.state['Hubs']['default']
    prev_email = config.state['Cloud']['email']
    yield
    print('State after test ({0}):'.format(config.state_path))
    config.dump()
    assert prev_path == config.state_path
    assert 'default' in config.state['Hubs'] and 'email' in config.state['Cloud'], 'State failed due to fixture.'
    assert prev_default == config.state['Hubs']['default']
    assert prev_email == config.state['Cloud']['email']
