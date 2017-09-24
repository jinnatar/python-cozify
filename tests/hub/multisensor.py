#!/usr/bin/env python3

from cozify import hub, multisensor, config
import sys, logging

def test_multisensor(conf_file):
    logging.basicConfig(level=logging.DEBUG)
    config.setStatePath(conf_file)

    data = hub.getDevices()
    print(multisensor.getMultisensorData(data))

if __name__ == "__main__":
    conf_file = None
    if len(sys.argv) > 1:
        conf_file = sys.argv[1]
    else:
        conf_file='/tmp/python-cozify-testing.cfg'
    test_multisensor(conf_file)
