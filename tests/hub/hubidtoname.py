#!/usr/bin/env python3
import sys, logging
from cozify import config, hub

def test_hub_id_to_name(conf_file, hub_id):
    logging.basicConfig(level=logging.DEBUG)
    config.setStatePath(conf_file)

    print(hub.getHubName(hub_id))

if __name__ == "__main__":
    conf_file = None
    hub_name = None
    if len(sys.argv) > 1:
        hub_id = sys.argv[1]
        if len(sys.argv) > 2:
            conf_file = sys.argv[1]
        else:
            conf_file='/tmp/python-cozify-testing.cfg'
    else:
        sys.exit(1)
    test_hub_id_to_name(conf_file, hub_id)
