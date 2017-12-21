#!/usr/bin/env python3
import sys
import requests
from cozify import hub, hub_api
from cozify.Error import APIError

def main(start=hub_api.apiPath):
    id = hub.getDefaultHub()
    host = hub.host(id)
    token = hub.token(id)
    api = start

    print('Testing against {0}, starting from {1}'.format(id, hub_api._getBase(host, api=start)))

    while True:
        base = hub_api._getBase(host, api=api)
        if not ping(base, token):
            print('Fail: {0}'.format(api))
        else:
            print('Works: {0}'.format(api))
            break
        api = increment(api)


def increment(apipath):
    base, section, version = apipath.split('/')
    next_version = round(float(version) + 0.1, 10)

    return '{0}/{1}/{2}'.format(base, section, next_version)

def ping(base, hub_token):
    headers = { 'Authorization': hub_token }
    call = '/hub/tz'
    response = requests.get(base + call, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
