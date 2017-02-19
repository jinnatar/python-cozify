import requests
from . import storage
from . import config as c

apiPath = '/cc/1.3/'

def getDevices():
    headers = {
        'Content-type': "application/json",
        'Accept': "application/json",
        'Authorization': c.config.get('Hub', 'authkey'),
        'Cache-control': "no-cache",
    }
    response = requests.get(_getBase() + 'devices', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None

def _getBase(host=c.ephemeral['Hub']['host'], port=c.config['Hub']['port']):
    if not c.ephemeral['Hub']['host']:
        if not cloud.authenticate():
            return None
    return 'http://%s:%s%s' % (host, port, apiPath)
        

# 1:1 implementation of /hub API call
# remoteToken: cozify Cloud remoteToken
# hubHost: valid ip/host to hub, defaults to ephemeral data
# returns map of hub state
def _hub(remoteToken, host=c.ephemeral['Hub']['host']):
    headers = {
            'Authorization': remoteToken
    }

    response = requests.get(_getBase(host=host) + 'hub', headers=headers)
    if response.status_code == 200:
        return json.loads(response.json)
    else:
        print(response.text)
        return None
