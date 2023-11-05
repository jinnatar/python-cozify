#!/usr/bin/env python3
import pprint
import sys

from cozify import hub
from cozify.test import debug


def main(device):
    hub.device_off(device)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
