#!/usr/bin/env python3
import sys, pprint
import jwt
from datetime import datetime


def main(token):
    pp = pprint.PrettyPrinter(indent=2)
    claims = jwt.decode(token, verify=False)
    for stamp in ['exp', 'iat']:
        ts = int(claims[stamp])
        claims[stamp] = '{0} #prettyprinted: {1}'.format(
            ts,
            datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

    pp.pprint(claims)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        sys.exit(1)
