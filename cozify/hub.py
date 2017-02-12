import requests
from . import storage
from . import config as c

hubBase='http://%s:%s/cc/1.3/' % (c.config.get('Hub', 'host'), c.config.get('Hub', 'port'))

def getDevices():
    headers = {
        'Content-type': "application/json",
        'Accept': "application/json",
        'Authorization': c.config.get('Hub', 'authkey'),
        'Cache-control': "no-cache",
    }
    response = requests.get(hubBase + 'devices', headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(response.text)
        return None
