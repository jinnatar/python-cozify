#!/usr/bin/env python3
"""Set high log level and consistent temporary state storage in /tmp/python-cozify-testing.cfg
"""

import logging
from cozify import config

logging.basicConfig(level=logging.DEBUG)

conf_file='/tmp/python-cozify-testing.cfg'
config.setStatePath(conf_file)
