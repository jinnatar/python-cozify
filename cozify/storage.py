from influxdb import InfluxDBClient
from influxdb import SeriesHelper

from . import config as c

db = InfluxDBClient(
        c.config.get('Storage', 'host'),
        c.config.get('Storage', 'port'),
        c.config.get('Storage', 'user'),
        c.config.get('Storage', 'password'),
        c.config.get('Storage', 'db')
)

class MultisensorSeries(SeriesHelper):
    class Meta:
        client = db
        series_name = 'multisensor'
        fields = ['temperature', 'humidity']
        tags = ['name']


# expects list of maps: [{name: 'foo', temperature: 42, humidity: 30}, ...]
def storeMultisensor(sensors):
    for sensor in sensors:
        MultisensorSeries(name=sensor['name'], temperature=sensor['temperature'], humidity=sensor['humidity'])
        print('%s, %s C, %s %%H' %(sensor['name'], sensor['temperature'], sensor['humidity']))
    MultisensorSeries.commit()
