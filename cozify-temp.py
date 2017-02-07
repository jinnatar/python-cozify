#!/usr/bin/python
import json, requests
from influxdb import InfluxDBClient
from influxdb import SeriesHelper

hub='cozify-hub-ip'
hubkey='insert-hub-key-here'

url = "http://%s:8893/cc/1.3/devices" % hub

headers = {
  'Content-type': "application/json",
  'Accept': "application/json",
  'Authorization': hubkey,
  'Cache-control': "no-cache",
}

response = requests.request("GET", url, headers=headers)
data = json.loads(response.text)

db = InfluxDBClient('localhost', '8086', 'root', 'root', 'cozify')

class TemperatureSeries(SeriesHelper):
    class Meta:
        client = db
        series_name = 'multisensor'
        fields = ['temperature', 'humidity']
        tags = ['name']


for device in data:
    name=data[device]['name']
    state=data[device]['state']
    devtype=state['type']

    if devtype == 'STATE_MULTI_SENSOR':
        temperature=state['temperature']
        if 'humidity' in state:
            humidity=state['humidity']
        else:
            humidity=None

        TemperatureSeries(name=name, temperature=temperature, humidity=humidity)
        print('%s, %s, %s' %(name, temperature, humidity))

print(TemperatureSeries._json_body_())
TemperatureSeries.commit()