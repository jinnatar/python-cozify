import requests, json
from . import config as c
from . import cloud

apiPath = '/cc/1.3/'

def getDevices(hubName=None):
    if hubName is None:
        # if hubName not provided, use default hub
        if 'default' not in c.ephemeral['Hubs']:
            print('no hub name given and no default known, running authentication')
            if not cloud.authenticate():
                print('Auth failed')
                return None # nothing we can do if auth failed
        hubName = c.ephemeral['Hubs']['default']

    configName = 'Hubs.' + hubName
    if configName not in c.ephemeral or 'hubtoken' not in c.ephemeral[configName]:
        print('Hub not known, auth needed first')
        if not cloud.authenticate():
            print('Auth failed')
            return None # nothing we can do if auth failed

    headers = {
        'Content-type': "application/json",
        'Accept': "application/json",
        'Authorization': c.ephemeral[configName]['hubtoken'],
        'Cache-control': "no-cache",
    }

    host = c.ephemeral[configName]['host']
    response = requests.get(_getBase(host=host) + 'devices', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def _getBase(host, port=8893, api=apiPath):
    # TODO(artanicus): this may still need some auth hook
    return 'http://%s:%s%s' % (host, port, api)


# 1:1 implementation of /hub API call
# remoteToken: cozify Cloud remoteToken
# hubHost: valid ip/host to hub, defaults to ephemeral data
# returns map of hub state
def _hub(remoteToken, host):
    headers = {
            'Authorization': remoteToken
    }

    response = requests.get(_getBase(host=host, api='/') + 'hub', headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(response.text)
        return None
