#!/usr/bin/env python3

import os, tempfile

from cozify import config
from cozify.test import debug
from cozify.test.fixtures import tmp_hub


def test_config_XDG(tmp_hub):
    assert config._initXDG()
    config.dump_state()


def test_config_XDG_env():
    with tempfile.TemporaryDirectory() as td:
        os.environ["XDG_CONFIG_HOME"] = td
        print('Overriden config: {0}, config.state_file: {1}'.format(td, config.state_file))
        assert config._initXDG()
        assert td in config.state_file
        config.dump_state()
