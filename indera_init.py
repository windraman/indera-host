from gpiozero import Button,LED
import requests
import json
from time import sleep
import os
#import mysql.connector
import sqlite3
import db_handler

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

#mydb = mysql.connector.connect(
 # host="localhost",
 # user="admin",
 # password="MYSQLn4n4cu",
 # database="inderadb"
#)

#mydb.autocommit = True

conn = sqlite3.connect(app_path + 'cgi-bin/inderasqlite3.db')
conn.row_factory = sqlite3.Row
db = conn.cursor()
 
def loadLogic():
    mycursor = conn.cursor()
    logicrows = mycursor.execute("SELECT * FROM logic").fetchall()
    myresult = json.loads(json.dumps( [dict(ix) for ix in logicrows]))
    
    return myresult
    

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
        print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
        print(str(e))   
    except requests.Timeout as e:
        print("OOPS!! Timeout Error")
        print(str(e))
    except requests.RequestException as e:
        print("OOPS!! General Error")
        print(str(e))        
    return res

url = "http://localhost:8080/send_sensor_value"

gpdicts = {}
modulslug = ""

gpdict = {}
temps = {}
sensors = []
logicarr = []

def setModulSlug(slug):
    global modulslug
    modulslug = slug
    
def getModulSlug():
    return modulslug

def check(list1, val):      
    # traverse in the list 
    for x in list1:   
        # compare with all the values 
        # with val 
        if val!= x: 
            return False 
    return True

def main():    
    pid = os.getpid()
    wpids(app_path + "pids/indera_init.pid",pid)

    jresp = db_handler.readme(True)
    jmodul = jresp['modul']
    gruparr = jmodul['grups']
    
    setModulSlug(jmodul['slug'])
    print(jmodul['slug'])

    
    def otomatis(dict):
        logicarr = loadLogic()
        print(str(logicarr))
        for logic in logicarr:
            kondisi = []
            jikaarr = json.loads(logic['jika'].replace("'", '"'))
            #print(str(jikaarr))
            for jika in jikaarr:
                if dict[jika['slug']].value == int(jika['nilai']):
                    kondisi.append(1)
                elif dict[jika['slug']].value != int(jika['nilai']):
                    kondisi.append(0)
                
            
            makaarr = json.loads(logic['maka'].replace("'", '"'))
            for maka in makaarr:
                if check(kondisi,1):                    
                    if int(maka['nilai'])==1:
                        dict[maka['slug']].on()
                        print(maka['slug'] + " on")
                        db_handler.send_sensor_value(maka['slug'],maka['nilai'],0,0)
                        #response = getHandler(url + "?slug="+maka['slug']+"&nilai="+maka['nilai']+"&ovrd=0")
                    elif int(maka['nilai'])==0:
                        dict[maka['slug']].off()
                        print(maka['slug'] + " off")
                        db_handler.send_sensor_value(maka['slug'],maka['nilai'],0,0)
                        #response = getHandler(url + "?slug="+maka['slug']+"&nilai="+maka['nilai']+"&ovrd=0")

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
                
            print("status " + sensor['name'] + " is " + str(temps[sensor['slug']]))
            wlogs(app_path+"logs/indera_init.log","status " + sensor['name'] + " is " + str(temps[sensor['slug']]))

    
    otomatis(gpdict)
                
    while True:
        for sensor in sensors:
            if sensor['tipe_pin']=='Button':
                if gpdict[sensor['slug']].is_pressed:
                    if gpdict[sensor['slug']].value!=temps[sensor['slug']]:
                        print(sensor['slug'] + ' pressed, temp = ' + str(temps[sensor['slug']]))
                        otomatis(gpdict)
                        db_handler.send_sensor_value(sensor['slug'],str(gpdict[sensor['slug']].value),0,0)
                        #response = requests.get(url + "?slug="+sensor['slug']+"&nilai=" + str(gpdict[sensor['slug']].value) + "&ovrd=0")
                        temps[sensor['slug']]=gpdict[sensor['slug']].value
                else:
                    if gpdict[sensor['slug']].value!=temps[sensor['slug']]:
                        print(sensor['slug'] + ' release, temp = ' + str(temps[sensor['slug']]))
                        otomatis(gpdict)
                        db_handler.send_sensor_value(sensor['slug'],str(gpdict[sensor['slug']].value),0,0)
                        #response = requests.get(url + "?slug="+sensor['slug']+"&nilai=" + str(gpdict[sensor['slug']].value) + "&ovrd=0")
                        temps[sensor['slug']]=gpdict[sensor['slug']].value
                
            
if __name__ == "__main__":
    main()

