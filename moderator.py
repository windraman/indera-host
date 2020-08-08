import requests
import json
from time import sleep
import os
import sys
import signal
import subprocess
from datetime import datetime
import sqlite3
import pathlib
app_path = os.path.dirname(os.path.realpath(__file__)) + "/"
print(os.path.dirname(os.path.realpath(__file__)))

status_service = "off"

aktif = False

services = ['server','indera_init','local_ovrd','cloud_ovrd']

def wlogs(f,s):
    file = open(app_path + "logs/" + f,"a")

    file.write(str(s)+"\n")
     
    file.close()

def check_pid(pid):
    #print("check" + str(pid))
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def wpids(f,s):
    file = open(app_path + "pids/" + f,"w")

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
    
def loadModul():
    conn = sqlite3.connect(app_path + 'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    mycursor = conn.cursor()
    modulrows = mycursor.execute("SELECT * FROM moduls").fetchone()
    myresult = dict(modulrows)
    
    return myresult

jmodul = loadModul()
modulslug = jmodul['slug']
status_service = jmodul['status_service']
print(status_service)

for s in services:
    now = datetime.now()
    file = open( app_path + "pids/" + s + '.pid', 'r')
    fline = file.readline()
    if fline != 'null':
        running = check_pid(int(fline))
    else:
        running = False

    print(str(s) + " is running " + str(running))
    wlogs("moderator.log",str(running))

    if status_service == "run" and running == False:
        if s == "server":
            os.system("nohup python3 " + app_path + s + ".py &")
            wlogs("moderator.log",str(now) + "---> " + s + " is running")
            response2 = getHandler("https://wahyu.top/public/api/notify_modul?slug=" + modulslug + "&pesan="+str(now)+ "-->Indera system " + modulslug + ", " + s + " service diaktifkan !")
            print(response2.content)
            aktif = True
        else:
            subprocess.Popen(["python3", app_path + s + ".py"])
            wlogs("moderator.log",str(now) + "---> " + s + " is running")
            response2 = getHandler("https://wahyu.top/public/api/notify_modul?slug=" + modulslug + "&pesan="+str(now)+ "-->Indera system " + modulslug + ", " + s + " service diaktifkan !")
            print(response2.content)
            aktif = True
    elif status_service == "off" and running:
        if s != "server":
            os.kill(int(fline), signal.SIGTERM)
            response2 = getHandler("https://wahyu.top/public/api/notify_modul?slug=" + modulslug + "&pesan="+str(now)+ "-->Indera system " + modulslug + ", " + s + " service di matikan !")
            print(response2.content)
            wlogs("moderator.log",str(now) + "---> " + s + " is terminated")
            wpids(s+".pid","null")
            aktif = False

    sleep(5)

sys.exit(0)
