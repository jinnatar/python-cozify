#!/usr/bin/env python3
import pprint
import sys

import jwt

from cozify import cloud, config, hub


def main(statepath):
    config.setStatePath(statepath)

    cloud_token = cloud.token()
    hub_id = hub.default()
    hub_token = hub.token(hub_id)

    pp = pprint.PrettyPrinter(indent=2)
    for token in cloud_token, hub_token:
        claims = jwt.decode(token, verify=False)
        pp.pprint(claims)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
