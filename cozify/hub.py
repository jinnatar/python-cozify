import requests, json
from . import config as c
from . import cloud

from .Error import APIError

apiPath = '/cc/1.3/'

def getDevices(hubName=None):
    if hubName is None:
        hubName = getDefaultHub()

    configName = 'Hubs.' + hubName
    if configName not in c.state or 'hubtoken' not in c.state[configName]:
        print('Hub not known, auth needed first')
        cloud.authenticate()

    # at this stage we have a valid name and auth
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
        raise APIError(response.status_code, response.text)

# return name of default Hub
# if default is unknown, run auth to make default known
def getDefaultHub():
    if 'default' not in c.state['Hubs']:
        print('no hub name given and no default known, running authentication')
        cloud.authenticate()
    return c.state['Hubs']['default']

def _getBase(host, port=8893, api=apiPath):
    # TODO(artanicus): this may still need some auth hook
    return 'http://%s:%s%s' % (host, port, api)

# perform a small API call to trigger any potential APIError and return boolean for success/failure
# TODO(artanicus): make the call actually small
def ping():
    try:
        getDevices()
    except APIError as e:
        if e.status_code == 401:
            return False
        else:
            raise
    else:
        return True


# 1:1 implementation of /hub API call
# hubHost: valid ip/host to hub, defaults to state data
# returns map of hub state
# interestingly enough remoteToken isn't needed here and the hub will answer regardless of auth
def _hub(host):
    response = requests.get(_getBase(host=host, api='/') + 'hub')
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise APIError(response.status_code, response.text)
