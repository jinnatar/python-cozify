#!/usr/bin/env python3
"""Set high log level
"""

import logging as dlog

from absl import logging

# shut up the hyperactive urllib3
urllib3_logger = dlog.getLogger("urllib3")
urllib3_logger.setLevel(dlog.CRITICAL)

logging.set_verbosity(logging.DEBUG)
