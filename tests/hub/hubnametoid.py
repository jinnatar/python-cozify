#!/usr/bin/env python3
import sys, logging
from cozify import config, hub

def test_hubnametoid(conf_file, hub_name):
    logging.basicConfig(level=logging.DEBUG)
    config.setStatePath(conf_file)

    print(hub.getHubId(hub_name))

if __name__ == "__main__":
    conf_file = None
    hub_name = None
    if len(sys.argv) > 1:
        conf_file = sys.argv[1]
        if len(sys.argv) > 2:
            hub_name = sys.argv[2]
        else:
            hub_name='Hubnester'
    else:
        conf_file='/tmp/python-cozify-testing.cfg'
    test_hubnametoid(conf_file, hub_name)
