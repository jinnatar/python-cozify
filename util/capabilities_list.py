#!/usr/bin/env python3                                                                                                                                         
from cozify import hub
from collections import OrderedDict

def sort(tosort):
    return list(OrderedDict.fromkeys(tosort))


def main():
    capabilities = []
    devs = hub.getDevices()
    for id, dev in devs.items():
        capabilities = capabilities + dev['capabilities']['values']

    gathered = sort(capabilities)
    implemented = sort([ e.name for e in hub.capability ])
    not_implemented = [item for item in gathered if item not in implemented]
    composite = sort(implemented + not_implemented)

    print('implemented ({0}): {1}'.format(len(implemented), implemented))
    print('gathered ({0}): {1}'.format(len(gathered), gathered))
    print('Not currently implemented ({0}): {1}'.format(len(not_implemented), not_implemented))
    print('Fully updated capabilities string: {0}'.format(' '.join(composite)))

if __name__ == "__main__":
        main()
