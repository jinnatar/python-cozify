#!/usr/bin/env python3
from pprint import PrettyPrinter

from cozify import hub

pp = PrettyPrinter()
pprint = pp.pprint


def main():
    test_devs = {}
    devs = hub.devices()
    for i, d in devs.items():
        if d["state"]["reachable"] and "test" in d["name"]:
            for cap in d["capabilities"]["values"]:
                if cap not in test_devs:
                    name = d["name"]
                    test_devs[cap] = f"{i}: {name}"

    pprint(test_devs)


if __name__ == "__main__":
    main()
