#!/usr/bin/env python3
import pprint
import sys

from cozify import hub, hub_api


def main(path):
    hub.ping()
    kwargs = {}
    hub._fill_kwargs(kwargs)
    response = hub_api.get(path, **kwargs)
    pprint.pprint(response)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
