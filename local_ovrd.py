#from gpiozero import Button,LED
import RPi.GPIO as GPIO

import requests
import json
from time import sleep
import os
from datetime import datetime
url2 = "http://wahyu.top/public/api/get_modul_info"
status_service = "off"
import sqlite3
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

mydb = sqlite3.connect(app_path + 'cgi-bin/inderasqlite3.db')
mydb.row_factory = sqlite3.Row
#mydb = conn.cursor()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def wlogs(f,s):
    file = open(f,"a")

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
        wlogs(app_path +"logs/local_ovrd.log","OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
        print(str(e))
    except requests.Timeout as e:
        wlogs(app_path +"logs/local_ovrd.log","OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        wlogs(app_path +"logs/local_ovrd.log","OOPS!! General Error")
        print(str(e))
        
    return res

pid = os.getpid()
wpids(app_path +"pids/local_ovrd.pid",pid)



def getSensorValue():
    global status_service
    sleep(0.5)
    now = datetime.now()
    mycursor = mydb.cursor()

    mycursor.execute('''SELECT sensor_value.*, sensors.pin, sensors.slug, sensors.name, tipe_pin.tipe_pin FROM sensor_value, sensors,
                    tipe_pin WHERE sensor_value.sensor_id = sensors.id AND sensors.tipe_sensor_id = tipe_pin.id AND is_read = 0 AND ovrd = 1''')

    myresult = mycursor.fetchall()
    try:
        #jresp = json.loads(response.content)
        #arrresp = jresp['sensor_value']
        for vs in myresult:
            if vs['tipe_pin']=="LED":
                print("overrided " + vs['slug'] + " local =" + vs['nilai'])
                GPIO.setup(vs['pin'],GPIO.OUT)
                #wlogs("/home/pi/GPIO/logs/local_ovrd.log","overrided " + vs['name'] + "=" + vs['nilai'])
                #setpival(vs['pin'],vs['nilai'])
                #slug = vs['slug']
                if(vs['nilai']=="1"):
                    GPIO.output(vs['pin'],GPIO.HIGH)
                else:
                    GPIO.output(vs['pin'],GPIO.LOW)

                myupdate = mydb.cursor()
                sql = "UPDATE sensor_value SET is_read = 1 WHERE id = '"+ str(vs['id']) +"'"
                myupdate.execute(sql)
                mydb.commit()     
                
            
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        wlogs(app_path +"logs/local_ovrd.log","Decoding JSON has failed")
        print ('Decoding JSON has failed')
        

while True:
    #print(mydb)
    getSensorValue()
    #import indera_init
    #print("modul " + indera_init.getModulSlug())