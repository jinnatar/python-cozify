from influxdb import InfluxDBClient
from influxdb import SeriesHelper

from . import config

# expects Cozify devices type json data
def getMultisensorData(data):
    out = []
    for device in data:
        state=data[device]['state']
        devtype = state['type']

        if devtype == 'STATE_MULTI_SENSOR':
            name=data[device]['name']

            if 'temperature' in state:
                temperature=state['temperature']
            else:
                temperature=None
            if 'humidity' in state:
                humidity=state['humidity']
            else:
                humidity=None

            out.append({
                    'name': name,
                    'temperature': temperature,
                    'humidity': humidity
                    })
    return out
