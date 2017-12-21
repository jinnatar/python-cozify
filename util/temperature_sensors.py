#!/usr/bin/env python3                                                                                                                                         
from cozify import hub
import pprint

def main():
    sensors = hub.devices(capability=hub.capability.TEMPERATURE)
    pprint.pprint(sensors)

if __name__ == "__main__":
    main()
