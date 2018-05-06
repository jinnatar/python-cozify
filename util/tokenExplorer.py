#!/usr/bin/env python3
import sys, pprint
import jwt

from cozify import hub, cloud, config


def main(statepath):
    config.set_state_path(statepath)

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
