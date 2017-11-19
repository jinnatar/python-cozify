#!/usr/bin/env python3
"""Set high log level and consistent temporary state storage in /tmp/python-cozify-testing.cfg
"""

import logging
from cozify import config

logging.basicConfig(level=logging.DEBUG)

# Disabled due to not wanting to mock the entire auth, so instead we use whatever is the live state.
#conf_file='/tmp/python-cozify-testing.cfg'
#config.setStatePath(conf_file)
