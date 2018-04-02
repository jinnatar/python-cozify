#!/usr/bin/env python3

from cozify import config
from cozify.test import debug


def test_config_XDG():
    print(config._initXDG())
