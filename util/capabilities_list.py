#!/usr/bin/env python3                                                                                                                                         
from cozify import hub
import cozify

def dedup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def main():
    capabilities = []
    devs = hub.devices()
    for id, dev in devs.items():
        capabilities = capabilities + dev['capabilities']['values']

    gathered = sorted(dedup(capabilities))
    implemented = [ e.name for e in hub.capability ]
    not_implemented = [ item for item in gathered if item not in implemented ]
    composite = sorted(implemented + not_implemented)

    print('Capabilities in python-cozify version {0}'.format(cozify.__version__))
    print('implemented ({0}): {1}'.format(len(implemented), implemented))
    print('gathered ({0}): {1}'.format(len(gathered), gathered))
    print('Not currently implemented ({0}): {1}'.format(len(not_implemented), not_implemented))
    print('Fully updated capabilities string({0}): {1}'.format(len(composite), ' '.join(composite)))

if __name__ == "__main__":
        main()
