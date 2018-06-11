#!/usr/bin/env python3

import pytest

import os, tempfile
from absl import logging

from cozify import config
from cozify.test import debug, state_verify
from cozify.test.fixtures import tmp_config, empty_config, live_config, tmp_hub, tmp_cloud


@pytest.mark.logic
def test_config_XDG(tmp_hub):
    assert config._initXDG()


@pytest.mark.destructive
def test_config_XDG_env(tmp_hub):
    with tempfile.TemporaryDirectory() as td:
        os.environ["XDG_CONFIG_HOME"] = td
        config.set_state_path(config._initXDG())
        assert td in config.state_path
    # we actually need to do some manual cleanup since this is very low level testing
    del os.environ["XDG_CONFIG_HOME"]
    config.set_state_path()
    logging.warn('Resetting state path back: {0}'.format(config.state_path))


@pytest.mark.logic
def test_config_state_copy(tmp_hub):
    with tempfile.NamedTemporaryFile() as tf:
        prev_state = config.state.items('Hubs')
        config.set_state_path(tf.name, copy_current=True)
        assert prev_state == config.state.items('Hubs')
        assert config.state['Hubs']['default'] == tmp_hub.id, 'Copied state was bad'


@pytest.mark.logic
def test_config_XDG_basedir(tmp_hub):
    # using mktemp deliberately to let _initXDG create it
    td = tempfile.mktemp()
    os.environ["XDG_CONFIG_HOME"] = td
    assert config._initXDG()
    assert os.path.isdir(td)
    os.removedirs(td + '/python-cozify')
    # we actually need to do some manual cleanup since this is very low level testing
    del os.environ["XDG_CONFIG_HOME"]


@pytest.mark.logic
def test_config_version(tmp_hub):
    assert config.version() == tmp_hub.meta_version


@pytest.mark.logic
def test_config_version_cold(tmp_hub):
    del config.state['meta']['version']
    config.commit()
    assert config.version() == 1
    del config.state['meta']
    config.commit()
    assert config.version() == 1
