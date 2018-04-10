lamp_ikea = {
    'capabilities': {
        'type':
            'SET',
        'values': [
            'IDENTIFY', 'ALERT', 'ON_OFF', 'CONTROL_LIGHT', 'COLOR_TEMP', 'BRIGHTNESS', 'DEVICE'
        ]
    },
    'groups': ['86397059-1341-4398-8274-3dcef21d0d54'],
    'id': 'd0bd9e1e-9857-4f57-ad53-bc9cbe667c35',
    'manufacturer': 'IKEA of Sweden',
    'model': None,
    'name': 'Table hanger 3',
    'room': ['87658ab7-bc4f-4d03-85a2-eb32ee1d4539'],
    'rwx': 509,
    'state': {
        'brightness': 0.1529,
        'colorMode': 'ct',
        'hue': -1,
        'isOn': True,
        'lastSeen': 1515949335273,
        'maxTemperature': 4000.0,
        'minTemperature': 2202.643171806167,
        'reachable': True,
        'saturation': -1,
        'temperature': 2202.643171806167,
        'transitionMsec': None,
        'type': 'STATE_LIGHT'
    },
    'timestamp': 1515949335281,
    'type': 'LIGHT',
    'zones': []
}

lamp_osram = {
    'capabilities': {
        'type':
            'SET',
        'values': [
            'IDENTIFY', 'ALERT', 'ON_OFF', 'CONTROL_LIGHT', 'TRANSITION', 'COLOR_TEMP',
            'BRIGHTNESS', 'DEVICE', 'COLOR_LOOP', 'COLOR_HS'
        ]
    },
    'description': None,
    'deviceType': None,
    'groups': [],
    'id': 'a371469c-ae3e-11e5-ab7a-68c90bba878f',
    'manufacturer': 'OSRAM',
    'model': 'Classic A60 RGBW',
    'name': 'Dining Täble',
    'room': ['87658ab7-bc4f-4d03-85a2-eb32ee1d4539'],
    'rwx': 509,
    'state': {
        'brightness': 0.4667,
        'colorMode': 'hs',
        'hue': 0.5061454830783556,
        'isOn': False,
        'lastSeen': 1508181980242,
        'maxTemperature': 6622.516556291391,
        'minTemperature': 2000.0,
        'reachable': False,
        'saturation': 1,
        'temperature': -1,
        'transitionMsec': None,
        'type': 'STATE_LIGHT'
    },
    'timestamp': 1515949468373,
    'type': 'LIGHT',
    'zones': []
}

strip_osram = {
    'capabilities': {
        'type':
            'SET',
        'values': [
            'IDENTIFY', 'ALERT', 'ON_OFF', 'CONTROL_LIGHT', 'TRANSITION', 'COLOR_TEMP',
            'BRIGHTNESS', 'DEVICE', 'COLOR_LOOP', 'COLOR_HS'
        ]
    },
    'groups': ['bc5eb203-1b98-491b-9184-6a855b344a32'],
    'id': '4bec213d-8319-4d02-ac2d-6cf34d80ae73',
    'manufacturer': 'OSRAM',
    'model': 'Flex RGBW',
    'name': 'JP Bookshelf',
    'room': ['be69e1df-b552-42cb-b9fb-eecf8c7087c7'],
    'rwx': 509,
    'state': {
        'brightness': 0.5297,
        'colorMode': 'hs',
        'hue': 0.2617993877991494,
        'isOn': True,
        'lastSeen': 1515949638592,
        'maxTemperature': 6622.516556291391,
        'minTemperature': 1501.5015015015015,
        'reachable': True,
        'saturation': 1,
        'temperature': -1,
        'transitionMsec': None,
        'type': 'STATE_LIGHT'
    },
    'timestamp': 1515949638596,
    'type': 'LIGHT',
    'zones': []
}

twilight_nexa = {
    'capabilities': {
        'type': 'SET',
        'values': ['DEVICE', 'TWILIGHT']
    },
    'description': None,
    'deviceType': None,
    'groups': [],
    'id': 'cd9bd0da-f1d5-11e5-8834-68c90bba878f',
    'manufacturer': 'Nexa',
    'model': 'Twilight Sensor',
    'name': 'Nexa Twilight 1',
    'room': [],
    'rwx': 509,
    'state': {
        'lastSeen': 1515845023652,
        'reachable': True,
        'twilight': True,
        'twilightStart': 1515845022577,
        'twilightStop': 1515832900640,
        'type': 'STATE_TWILIGHT'
    },
    'timestamp': 1515845023656,
    'type': 'TWILIGHT',
    'zones': []
}

plafond_osram = {
    'capabilities': {
        'type':
            'SET',
        'values': [
            'IDENTIFY', 'ALERT', 'ON_OFF', 'CONTROL_LIGHT', 'TRANSITION', 'COLOR_TEMP',
            'BRIGHTNESS', 'DEVICE'
        ]
    },
    'groups': [],
    'id': '720b5285-06a3-4069-81e1-519d5b45048d',
    'manufacturer': 'OSRAM',
    'model': 'Surface Light TW',
    'name': 'Lower Stairway',
    'room': ['87658ab7-bc4f-4d03-85a2-eb32ee1d4539'],
    'rwx': 509,
    'state': {
        'brightness': 0,
        'colorMode': 'ct',
        'hue': -1,
        'isOn': False,
        'lastSeen': 1515951870541,
        'maxTemperature': 6535.9477124183,
        'minTemperature': 2702.7027027027025,
        'reachable': True,
        'saturation': -1,
        'temperature': 2702.7027027027025,
        'transitionMsec': None,
        'type': 'STATE_LIGHT'
    },
    'timestamp': 1515951870545,
    'type': 'LIGHT',
    'zones': []
}

state_clean = {
    'brightness': None,
    'colorMode': None,
    'hue': None,
    'isOn': None,
    'lastSeen': None,
    'maxTemperature': None,
    'minTemperature': None,
    'reachable': None,
    'saturation': None,
    'temperature': None,
    'transitionMsec': None,
    'type': 'STATE_LIGHT'
}

devices = {
    lamp_ikea['id']: lamp_ikea,
    lamp_osram['id']: lamp_osram,
    strip_osram['id']: strip_osram,
    plafond_osram['id']: plafond_osram,
    twilight_nexa['id']: twilight_nexa
}

device_ids = {
    'lamp_ikea': lamp_ikea['id'],
    'lamp_osram': lamp_osram['id'],
    'strip_osram': strip_osram['id'],
    'plafond_osram': plafond_osram['id'],
    'twilight_nexa': twilight_nexa['id'],
    'reachable': plafond_osram['id'],
    'not-reachable': lamp_osram['id']
}

states = {'dirty': lamp_ikea['state'], 'clean': state_clean}
