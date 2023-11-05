#!/usr/bin/env python3
import pprint
import sys

from cozify import hub


def main(device):
    devs = hub.devices()
    pprint.pprint(devs[device])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
