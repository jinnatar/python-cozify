#!/usr/bin/env python3
from cozify import hub
import sys


def main(capability=None):
    devs = None
    if capability:
        devs = hub.devices(capabilities=hub.capability[capability])
    else:
        devs = hub.devices()

    for key, dev in devs.items():
        print('{0}: {1}'.format(key, dev['name']))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
