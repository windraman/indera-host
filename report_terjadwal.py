from gpiozero import Button,LED
import requests
import json
from time import sleep
import os
import datetime

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

def wlogs(f,s):
    file = open(f,"w")

    file.write(str(s) + "\n")
     
    file.close()
    
def wpids(f,s):
    file = open(f,"w")

    file.write(str(s))
     
    file.close()
    
def getHandler(url):
    res = []
    try:
        res = requests.get(url,timeout=7.0)
    except requests.ConnectionError as e:
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))   
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("OOPS!! General Error")
        print(str(e))        
    return res

url = "http://localhost/indera/public/api/send_sensor_value"
gpdict = {}
temps = {}
sensors = []
logicarr = []

response = getHandler("http://localhost/indera/public/api/readme?content=raspindera")
jresp = json.loads(response.content)
jmodul = jresp['modul']
gruparr = jmodul['grups']

pesan = "[Laporan Harian " +datetime.datetime.now().strftime('%b %d %Y %H:%M:%S') + "]" + jmodul['name'] + ", lokasi : " + jmodul['lokasi']

for grup in gruparr:
    sensorarr = grup['sensors']
    for sensor in sensorarr:
        sensors.append(sensor)
        if  sensor['tipe_pin']=='LED':
            gpdict[sensor['slug']] = LED(int(sensor['pin']))
            temps[sensor['slug']] = gpdict[sensor['slug']].value
        elif  sensor['tipe_pin']=='Button':
            gpdict[sensor['slug']] = Button(int(sensor['pin']))
            temps[sensor['slug']] = gpdict[sensor['slug']].value
        
        pesan = str(pesan) + "," + str(sensor['name']) + ":" + str(gpdict[sensor['slug']].value)
            
print(pesan)
wlogs(app_path + "logs/report_terjadwal.log",pesan)
response2 = getHandler("http://wahyu.top/public/api/notify_modul?slug=" + jmodul['slug'] + "&pesan=" + pesan)
  

