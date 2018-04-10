import time

from . import config


# expects Cozify devices type json data
def getMultisensorData(data):  # pragma: no cover
    """Deprecated, will be removed in v0.3
    """
    out = []
    for device in data:
        state = data[device]['state']
        devtype = state['type']

        if devtype == 'STATE_MULTI_SENSOR':
            name = data[device]['name']
            if 'lastSeen' in state:
                timestamp = state['lastSeen']
            else:
                # if no time of measurement is known we must make a reasonable assumption
                # Stored here in milliseconds to match accuracy of what the hub will give you
                timestamp = time.time() * 1000
            if 'temperature' in state:
                temperature = state['temperature']
            else:
                temperature = None
            if 'humidity' in state:
                humidity = state['humidity']
            else:
                humidity = None

            out.append({
                'name': name,
                'time': timestamp,
                'temperature': temperature,
                'humidity': humidity
            })
    return out
