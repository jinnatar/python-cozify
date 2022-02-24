#!/usr/bin/env python3
from cozify import hub
import sys
from pprint import PrettyPrinter

pp = PrettyPrinter()
pprint = pp.pprint


def main():
    test_devs = {}
    caps = [cap.name for cap in hub.capability]
    devs = hub.devices()
    for i, d in devs.items():
        if d['state']['reachable'] and 'test' in d['name']:
            for cap in d['capabilities']['values']:
                if cap not in test_devs:
                    name = d['name']
                    test_devs[cap] = f'{i}: {name}'

    pprint(test_devs)


if __name__ == "__main__":
    main()
