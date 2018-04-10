#!/usr/bin/env python3

import pytest

import os, tempfile

from cozify import config
from cozify.test import debug
from cozify.test.fixtures import tmp_hub, tmp_cloud


@pytest.mark.logic
def test_config_XDG(tmp_hub):
    assert config._initXDG()


@pytest.mark.logic
def test_config_XDG_env(tmp_hub):
    with tempfile.TemporaryDirectory() as td:
        os.environ["XDG_CONFIG_HOME"] = td
        config.setStatePath(config._initXDG())
        assert td in config.state_file


@pytest.mark.logic
def test_config_XDG_basedir(tmp_hub):
    # using mktemp deliberately to let _initXDG create it
    td = tempfile.mktemp()
    os.environ["XDG_CONFIG_HOME"] = td
    assert config._initXDG()
    assert os.path.isdir(td)
    os.removedirs(td + '/python-cozify')
