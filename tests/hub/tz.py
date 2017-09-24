#!/usr/bin/env python3

from cozify import hub, config
import sys, logging

def test_tz(conf_file):
    logging.basicConfig(level=logging.DEBUG)
    config.setStatePath(conf_file)
    hub.ping()
    hubSection = 'Hubs.' + config.state['Hubs']['default']
    print(hub._tz(
        host=config.state[hubSection]['host'],
        hub_token=config.state[hubSection]['hubtoken'],
        cloud_token=config.state['Cloud']['remotetoken']
        ))

if __name__ == "__main__":
    conf_file = None
    if len(sys.argv) > 1:
        conf_file = sys.argv[1]
    else:
        conf_file='/tmp/python-cozify-testing.cfg'
    test_tz(conf_file)
