# python-cozify
Unofficial Python3 API bindings for the (unpublished) Cozify API. Includes 1:1 API calls plus helper functions to string together an authentication flow.

## Installation
The recommended way is to install from PyPi:
```bash
   sudo -H pip3 install cozify
```
or clone this repo (master branch may contain unstable features!) and:
```bash
   sudo python3 setup.py install
```


## Basic usage
### read devices, extract multisensor data
```python
from cozify import hub, multisensor
devices = hub.getDevices()
print(multisensor.getMultisensorData(devices))
```
### only authenticate
```python
from cozify import cloud
cloud.authenticate()
# authenticate() is interactive and usually triggered automatically
# authentication data is stored in ~/.config/python-cozify.cfg
```
### authenticate with a non-default state storage
```python
from cozify import cloud, config
config.setStatePath('/tmp/testing-state.cfg')
cloud.authenticate()
# authentication and other useful data is now stored in the defined location instead of ~/.config/python-cozify.cfg
```

## Current limitations
* Right now tokens are assumed to never expire and their functionality is not questioned.
* For now there are only read calls. New API call requests are welcome as issues or pull requests!
* authentication flow is as automatic as possible but still a bit fragile. Any reported issues are very welcome.

## Sample projects
* [github.com/Artanicus/cozify-temp](https://github.com/Artanicus/cozify-temp) - Store Multisensor data into InfluxDB
* Report an issue to get your project added here
