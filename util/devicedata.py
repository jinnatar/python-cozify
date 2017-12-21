#!/usr/bin/env python3                                                                                                                                         
from cozify import hub
import pprint, sys

def main(device):
    devs = hub.getDevices()
    pprint.pprint(devs[device])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
