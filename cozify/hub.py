import requests, json
from . import config as c
from . import cloud

apiPath = '/cc/1.3/'

def getDevices(hubName=None):
    if hubName is None:
        # if hubName not provided, use default hub
        if 'default' not in c.state['Hubs']:
            print('no hub name given and no default known, running authentication')
            if not cloud.authenticate():
                print('Auth failed')
                return None # nothing we can do if auth failed
        hubName = c.state['Hubs']['default']

    configName = 'Hubs.' + hubName
    if configName not in c.state or 'hubtoken' not in c.state[configName]:
        print('Hub not known, auth needed first')
        if not cloud.authenticate():
            print('Auth failed')
            return None # nothing we can do if auth failed

    headers = {
        'Content-type': "application/json",
        'Accept': "application/json",
        'Authorization': c.state[configName]['hubtoken'],
        'Cache-control': "no-cache",
    }

    host = c.state[configName]['host']
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
# hubHost: valid ip/host to hub, defaults to state data
# returns map of hub state
# interestingly enough remoteToken isn't needed here and the hub will answer regardless of auth
def _hub(host):
    response = requests.get(_getBase(host=host, api='/') + 'hub')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(response.text)
        return None
