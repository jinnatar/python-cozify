#!/usr/bin/env python3
from cozify import hub, cloud, hub_api

from cozify.test import debug

def main():
    hub_id = hub.default()

    print(hub_api.tz(
            host = hub.host(hub_id),
            cloud_token = cloud.token(),
            hub_token = hub.token(hub_id),
            remote = True
            ))

if __name__ == "__main__":
        main()
