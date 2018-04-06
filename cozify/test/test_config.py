#!/usr/bin/env python3

import os, tempfile

from cozify import config
from cozify.test import debug
from cozify.test.fixtures import tmp_hub


def test_config_XDG(tmp_hub):
    assert config._initXDG()


def test_config_XDG_env(tmp_hub):
    with tempfile.TemporaryDirectory() as td:
        os.environ["XDG_CONFIG_HOME"] = td
        config.setStatePath(config._initXDG())
        assert td in config.state_file
