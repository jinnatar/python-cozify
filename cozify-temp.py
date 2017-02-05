#!/usr/bin/python                                                                                                                                              
import json, requests                                                                                                                                          
from influxdb import InfluxDBClient                                                                                                                            
from influxdb import SeriesHelper                                                                                                                              
                                                                                                                                                               
url = "http://10.0.10.147:8893/cc/1.3/devices"                                                                                                                 
                                                                                                                                                               
headers = {                                                                                                                                                    
        'Content-type': "application/json",                                                                                                                    
        'Accept': "application/json",                                                                                                                          
        'Authorization': "device-key",                                                                               
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
    state=data[device]['state']                                                                                                                                
    name=data[device]['name']                                                                                                                                  
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