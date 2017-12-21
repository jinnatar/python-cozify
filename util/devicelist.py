#!/usr/bin/env python3                                                                                                                                         
from cozify import hub

def main():
    devs = hub.getDevices()

    for key, dev in devs.items():
        print('{0}: {1}'.format(key, dev['name']))

if __name__ == "__main__":
        main()
