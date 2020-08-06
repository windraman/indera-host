import RPi.GPIO as GPIO
import requests
import json
from time import sleep
import os
from datetime import datetime
url2 = "http://wahyu.top/public/api/get_modul_info"
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"
import sqlite3
import db_handler

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def wlogs(f,s):
    file = open(app_path + "logs/" + f,"a")

    file.write(str(s) + "\n")
     
    file.close()
    
def wpids(f,s):
    file = open(app_path+ "pids/" + f,"w")

    file.write(str(s))
     
    file.close()
    
def getHandler(url):
    res = []
    try:
        res = requests.get(url,timeout=7.0)
    except requests.ConnectionError as e:
        wlogs("cloud_ovrd.log","OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
        print(str(e))
    except requests.Timeout as e:
        wlogs("cloud_ovrd.log","OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        wlogs("cloud_ovrd.log","OOPS!! General Error")
        print(str(e))
    except:
        wlogs("cloud_ovrd.log","Something wrong")
        print(str(e))
    return res

pid = os.getpid()
wpids("cloud_ovrd.pid",pid)

def loadModul():
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    mycursor = conn.cursor()
    modulrows = mycursor.execute("SELECT * FROM moduls").fetchone()
    myresult = dict(modulrows)
    
    return myresult

jmodul = loadModul()
modulslug = jmodul['slug']


def getSensorValue(url,slug,ovrd,is_read,batas):
    sleep(7)
    now = datetime.now()
    response = getHandler(url + "?slug=" + slug + "&ovrd=" + ovrd + "&is_read=" +is_read + "&batas=" + batas)
    print(response)
    try:
        jresp = json.loads(response.content)
        #print(str(jresp))
        arrresp = jresp['sensor_value']
        for vs in arrresp:            
            if vs['tipe_pin']=="LED":
                print("overrided " + vs['slug'] + " cloud =" + vs['nilai'])
                GPIO.setup(vs['pin'],GPIO.OUT)
                wlogs("cloud_ovrd.log",str(now) + "->overrided " + vs['name'] + "=" + vs['nilai'])
                if(vs['nilai']=="1"):
                    GPIO.output(vs['pin'],GPIO.HIGH)
                    db_handler.send_sensor_value(vs['slug'],vs['nilai'],1,1)
                else:
                    GPIO.output(vs['pin'],GPIO.LOW)
                    db_handler.send_sensor_value(vs['slug'],vs['nilai'],1,1)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print ('Decoding JSON has failed')
        wlogs("cloud_ovrd.log",str(now) + "-> Value Error")
    

while True:    
    getSensorValue(url2,modulslug,"1","0","10")