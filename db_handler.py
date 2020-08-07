import sqlite3
import json
import socket
import fcntl
import struct
import time
import requests
import unidecode
import re
import os
from urllib.parse import urlparse, unquote_plus, urlencode

app_path = os.path.dirname(os.path.realpath(__file__)) + "/"

url = "https://wahyu.top/public/api/"

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
    except OSError:
        return 0

def getWlan():
    local_ip = get_ip_address('wlan0')
    if local_ip == 0:
        local_ip = get_ip_address('eth0')
    return local_ip


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

def postHandler(url,myobj):
    res = []
    try:
        res = requests.post(url,json=myobj)
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

def slugify(text):
    text = unidecode.unidecode(text).lower()
    return re.sub(r'[\W_]+', '_', text)

def reqslug(id,permisi):
    mresp = getHandler(url + "my_modul?id="+id+"&permisi="+permisi)
    jresp = json.loads(mresp.content)
    
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    umodul = {}
    try:
        rows = db.execute('''UPDATE moduls SET slug = "''' + jresp['newslug'] + '''", owner_id = "''' + id + '''", status_service = "run"''')
        conn.commit()
        
        umodul = dict(rows)
        umodul['api_status'] = 1
    except sqlite3.OperationalError:
        umodul['error'] = sqlite3.OperationalError
        umodul['api_status'] = 0
    
    
    conn.close()
    
    
    return jresp

def readme( json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''
    SELECT * from moduls
    ''').fetchone()    

    if json_str:
        jmlsensor = 0
        jmodul = dict()
        jmodul['modul'] = dict(rows)
        grups = db.execute('''
            SELECT * from grups WHERE moduls_id = "''' + str(rows['id']) + '''"''').fetchall()
        
        jgrup = json.loads(json.dumps( [dict(ix) for ix in grups] ))
        
        for gp in jgrup:
            sensors = db.execute('''
                    SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                    WHERE sensors.tipe_sensor_id = tipe_pin.id AND
                    sensors.grups_id = "''' + str(gp['id']) + '''"''').fetchall()                
            
            jsensor = json.loads(json.dumps( [dict(ix) for ix in sensors] ))
            
            gp['sensors'] = jsensor
            gp['jsensor'] = len(jsensor)
            jmlsensor += len(jsensor)
            
        jmodul['modul']['ip_address'] = getWlan()
        jmodul['modul']['grups'] = jgrup
        jmodul['modul']['jgrup'] = len(jgrup)
        jmodul['modul']['jsensor'] = jmlsensor
        
        tipe = db.execute('''
                SELECT * from tipe_pin''').fetchall()
            
        jmodul['tipe_pin'] = json.loads(json.dumps( [dict(ix) for ix in tipe] ))
        
        
        conn.commit()
        conn.close()
        
        return jmodul
    
    conn.commit()
    conn.close()

    return rows
        

def get_modul( slug, json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''
    SELECT * from moduls
    WHERE slug = "''' + slug + '''"
    ''').fetchone()    

    if json_str:
        jmlsensor = 0
        jmodul = dict(rows)
        grups = db.execute('''
            SELECT * from grups WHERE moduls_id = "''' + str(rows['id']) + '''"''').fetchall()
        
        jgrup = json.loads(json.dumps( [dict(ix) for ix in grups] ))
        
        for gp in jgrup:            
            sensors = db.execute('''
                SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                WHERE sensors.tipe_sensor_id = tipe_pin.id AND
                sensors.grups_id = "''' + str(gp['id']) + '''"''').fetchall()
            
            jsensor = json.loads(json.dumps( [dict(ix) for ix in sensors] ))
            
            gp['sensors'] = jsensor
            gp['jsensor'] = len(jsensor)
            jmlsensor += len(jsensor)
        
        jmodul['grups'] = jgrup
        jmodul['ip_address'] = getWlan()
        jmodul['jgrup'] = len(jgrup)
        jmodul['jsensor'] = jmlsensor
        
        conn.commit()
        conn.close()
        
        return jmodul
    
    conn.commit()
    conn.close()

    return rows

def get_sensors( slug, get_grup, json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()   
    jgrup = {}
    if json_str:
        if get_grup == "1":
            rows = db.execute('''SELECT * from grups WHERE slug = "''' + slug + '''"''').fetchone()
            jgrup = dict(rows)
            sensors = db.execute('''SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                    WHERE sensors.tipe_sensor_id = tipe_pin.id AND
                    sensors.grups_id = "''' + str(jgrup['id']) + '''"''').fetchall()
            jsensor = json.loads(json.dumps( [dict(ix) for ix in sensors] )) 
            for sensor in jsensor:            
                sensor_value = db.execute('''
                    SELECT * FROM sensor_value
                    WHERE sensor_id = "''' + str(sensor['id']) + '''" ORDER BY id DESC''').fetchone()
                if sensor_value is None:
                    jsensor_value = {}
                    sensor['last_db_value'] = jsensor_value
                    sensor['sensor_value'] = "null"
                    sensor['actual_pin_value'] = "null"
                else:
                    jsensor_value = dict(sensor_value)
                    sensor['last_db_value'] = jsensor_value
                    sensor['sensor_value'] = jsensor_value['nilai']
                    sensor['actual_pin_value'] = jsensor_value['nilai']
                    
            jgrup['sensors'] = jsensor
            jgrup['jsensor'] = len(jsensor)
        else:
            sensors = db.execute('''
                    SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                    WHERE sensors.tipe_sensor_id = tipe_pin.id''').fetchall()
            jsensor = json.loads(json.dumps( [dict(ix) for ix in sensors] )) 
            
            for sensor in jsensor:            
                sensor_value = db.execute('''
                    SELECT * FROM sensor_value
                    WHERE sensor_id = "''' + str(sensor['id']) + '''" ORDER BY id DESC''').fetchone()
                if sensor_value is None:
                    jsensor_value = {}
                    sensor['last_db_value'] = jsensor_value
                    sensor['sensor_value'] = "null"
                    sensor['actual_pin_value'] = "null"
                else:
                    jsensor_value = dict(sensor_value)
                    sensor['last_db_value'] = jsensor_value
                    sensor['sensor_value'] = jsensor_value['nilai']
                    sensor['actual_pin_value'] = jsensor_value['nilai']                
            jgrup['sensors'] = jsensor
            jgrup['jsensor'] = len(jsensor)              
        
        
        conn.commit()
        conn.close()
        
        return jgrup
    
    conn.commit()
    conn.close()

    return rows

def get_sensor_value( slug, batas, json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''
    SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
    WHERE sensors.tipe_sensor_id = tipe_pin.id AND slug = "''' + slug + '''"''').fetchone()    

    if json_str:
        jsensor = dict(rows)
        if batas == "1":
            sensor_value = db.execute('''
                SELECT * FROM sensor_value
                WHERE sensor_id = "''' + str(jsensor['id']) + '''"
                ORDER BY id DESC''').fetchone()
            if sensor_value is None:
                jsensor_value = {}
                jsensor['last_db_value'] = jsensor_value
                jsensor['sensor_value'] = "null"
                jsensor['actual_pin_value'] = "null"
            else:
                jsensor_value = dict(sensor_value)
                jsensor['last_db_value'] = jsensor_value
                jsensor['sensor_value'] = jsensor_value['nilai']
                jsensor['actual_pin_value'] = jsensor_value['nilai']
        else:
            sensor_value = db.execute('''
                SELECT * FROM sensor_value
                WHERE sensor_id = "''' + str(jsensor['id']) + '''"
                ORDER BY id DESC LIMIT ''' + batas).fetchall()
            if sensor_value is None:
                jsensor_value = {}
                jsensor['last_db_value'] = jsensor_value
                jsensor['sensor_value'] = "null"
                jsensor['actual_pin_value'] = "null"
            else:    
                jsensor_value = json.loads(json.dumps( [dict(ix) for ix in sensor_value] ))
                jsensor['last_db_value'] = jsensor_value
                jsensor['sensor_value'] = "null"
                jsensor['actual_pin_value'] = "null"
            
        
        conn.commit()
        conn.close()
        
        return jsensor
    
    conn.commit()
    conn.close()

    return rows

def set_noc( id, noc):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    try:
        rows = db.execute('''UPDATE sensors SET noc = ''' + noc + ''' 
            WHERE id = "''' + id + '''"''')
        conn.commit()
        
        jnoc = dict(rows)
        jnoc['api_status'] = 1
    except sqlite3.OperationalError:
        jnoc['api_status'] = 0
    
    
    conn.close()

    return jnoc

def send_sensor_value( slug, nilai, ovrd, is_read):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                WHERE sensors.tipe_sensor_id = tipe_pin.id AND slug = "''' + slug + '''"''').fetchone()    
    conn.commit()
    jsensor = dict(rows)
    sql = '''INSERT INTO sensor_value(sensor_id,nilai,ovrd,is_read) VALUES ('''+ str(jsensor['id']) +''',''' + str(nilai) + ''','''+ str(ovrd) + ''',''' + str(is_read) + ''')'''
    try:
        db = conn.cursor()
        db.execute(sql)
        conn.commit()
        
        jsensor ['api_status'] = 1
    except sqlite3.OperationalError:
        jsensor['api_status'] = 0        
    
    conn.close()
    
    if jsensor['api_status'] == 1 and jsensor['noc'] == 1 and is_read == "0":
        #send to cloud
        cresp = getHandler(url + "sensor_value?slug="+str(slug)+"&nilai="+str(nilai)+"&ovrd="+str(ovrd)+"&is_read=1")
        #jsensor['cloud'] = cresp
        

    return jsensor

def update_sensor( slug, name, pin, pin2, tipe_sensor_id, parentslug):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    try:
        rows = db.execute('''UPDATE sensors SET slug = "''' + slugify(parentslug + '_' + name) + '''"'''
            + ''',name="''' + name + '''",pin = '''+ str(pin) + ''', pin2 = ''' + str(pin2) + ''', tipe_sensor_id = ''' + str(tipe_sensor_id) + '''
            WHERE slug = "''' + slug + '''"''')
        conn.commit()
        
        usensor = dict(rows)
        usensor['api_status'] = 1
    except sqlite3.OperationalError:
        usensor['api_status'] = 0
    
    
    conn.close()

    return usensor

def update_grup( slug, name, parentslug):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    try:
        rows = db.execute('''UPDATE grups SET slug = "''' + slugify(parentslug + '_' + name) + '''"'''
            + ''',name="''' + name + '''"
            WHERE slug = "''' + slug + '''"''')
        conn.commit()
        
        ugrup = dict(rows)
        ugrup['api_status'] = 1
    except sqlite3.OperationalError:
        ugrup['api_status'] = 0
    
    
    conn.close()

    return ugrup

def update_modul( slug, name, lokasi, latitude, longitude):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    umodul = {}
    try:
        rows = db.execute('''UPDATE moduls SET name = "''' + name + '''"'''
            + ''',lokasi="''' + lokasi + '''",latitude="''' + latitude + '''",longitude="'''+ longitude + '''" 
            WHERE slug = "''' + slug + '''"''')
        conn.commit()
        
        umodul = dict(rows)
        umodul['api_status'] = 1
    except sqlite3.OperationalError:
        umodul['error'] = sqlite3.OperationalError
        umodul['api_status'] = 0
    
    
    conn.close()

    return umodul

def set_service( slug, status_service):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    try:
        rows = db.execute('''UPDATE moduls SET status_service = "''' + status_service + '''"
                WHERE slug = "''' + slug + '''"''')
        conn.commit()
        
        umodul = dict(rows)
        umodul['api_status'] = 1
    except sqlite3.OperationalError:
        umodul['api_status'] = 0
    
    
    conn.close()

    return umodul

def get_logic( slug, logicslug, json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''SELECT * FROM moduls WHERE slug = "''' + slug + '''"''').fetchone()

    if json_str:
        jmodul = dict(rows)
        if len(logicslug) == 0:
            logics = db.execute('''
                SELECT * FROM logic''').fetchall()
            jlogic = json.loads(json.dumps( [dict(ix) for ix in logics] ))
        else:
            logics = db.execute('''
                SELECT * FROM logic WHERE slug="''' + logicslug + '''"''').fetchone()
            
            jlogic = dict(logics)
            jika = json.loads(jlogic['jika'].replace("'", '"'))
            jlogic['jjika'] = []
            for jk in jika:
                jikarows = db.execute('''SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                    WHERE sensors.tipe_sensor_id = tipe_pin.id AND slug = "''' + jk['slug'] + '''"''').fetchone()
                djika = dict(jikarows)
                
                djika['last_db_value'] = jk['nilai']
                jlogic['jjika'].append(djika)
                
            
            maka = json.loads(jlogic['maka'].replace("'", '"'))
            jlogic['jmaka'] = []
            for mk in maka:
                makarows = db.execute('''SELECT sensors.* ,tipe_pin.tipe_pin, tipe_pin.io FROM sensors,tipe_pin
                    WHERE sensors.tipe_sensor_id = tipe_pin.id AND slug = "''' + mk['slug'] + '''"''').fetchone()
                dmaka = dict(makarows)
                
                dmaka['last_db_value'] = mk['nilai']
                jlogic['jmaka'].append(dmaka)
                
        
        jmodul['logic'] = jlogic
        
        
        conn.commit()
        conn.close()
        
        return jmodul
    
    conn.commit()
    conn.close()

    return rows

def add_logic(name,jika,maka):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    jlogic = {}
    try:
        sql = '''INSERT INTO logic (slug,name,jika,maka) VALUES("''' + slugify(name) + '''", "''' + name + '''"
                , "''' + jika + '''", "''' + maka + '''")'''
        print(sql)
        rows = db.execute(sql)
        conn.commit()
        
        jlogic = dict(rows)
        jlogic['api_status'] = 1
    except sqlite3.OperationalError:
        jlogic['api_status'] = 0
    
    
    conn.close()

    return jlogic


def update_logic(id,name,jika,maka):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    jlogic = {}
    try:
        sql = '''UPDATE logic SET slug = "''' + slugify(name) + '''", name = "''' + name + '''", jika = "''' + jika + '''", maka = "''' + maka + '''"  
            WHERE id = "''' + id + '''"'''
        print(sql)
        rows = db.execute(sql)
        conn.commit()
        
        jlogic = dict(rows)
        jlogic['api_status'] = 1
    except sqlite3.OperationalError:
        jlogic['api_status'] = 0
    
    
    conn.close()

    return jlogic

def rem_logic(slug):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    ulogic = {}
    try:
        sql = '''DELETE FROM logic WHERE slug = "''' + slug + '''"'''
        print(sql)
        rows = db.execute(sql)
        conn.commit()
        
        ulogic = dict(rows)
        ulogic['api_status'] = 1
    except sqlite3.OperationalError:
        ulogic['api_status'] = 0
    
    
    conn.close()

    return ulogic

def sync_modul( slug, json_str = False ):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''
    SELECT * from moduls
    WHERE slug = "''' + slug + '''"
    ''').fetchone()    

    if json_str:
        jmodul = dict(rows)
        grups = db.execute('''
            SELECT id,slug,name from grups WHERE moduls_id = "''' + str(rows['id']) + '''"''').fetchall()
        
        jgrup = json.loads(json.dumps( [dict(ix) for ix in grups] ))
        
        for gp in jgrup:            
            sensors = db.execute('''
                SELECT slug,name,pin,pin2,tipe_sensor_id FROM sensors
                WHERE grups_id = "''' + str(gp['id']) + '''"''').fetchall()
            
            jsensor = json.loads(json.dumps( [dict(ix) for ix in sensors] ))
            
            gp['sensors'] = jsensor
        
        jmodul['grups'] = jgrup
        jmodul['ip_address'] = getWlan()
        
        conn.commit()
        
        data = {'slug':rows['slug'],'name':rows['name'],'lokasi':rows['lokasi'],'owner':rows['owner_id'],'local_ip':getWlan(),
                'latitude':rows['latitude'],'longitude':rows['longitude'],'grup_json':str(jgrup)} #jgrup
        #print(jgrup)        
        sresp = postHandler(url + "sync_modul", data)
        print(sresp.content)
        try:
            jsync = json.loads(sresp.content)
            jmodul['sync_modul_id'] = jsync['id']
        except json.decoder.JSONDecodeError:
            jmodul['sync_modul_id'] = "null"
            
        conn.close()
        
        return jmodul
    
    conn.commit()
    conn.close()

    return rows

def new_grup( slug, name):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''SELECT * FROM moduls WHERE slug = "''' + slug + '''"''').fetchone()

    try:
        jmodul = dict(rows)
        newgrup = db.execute('''
            INSERT INTO grups(slug,name,moduls_id) VALUES ("'''+ slugify(slug + "_" + name ) +  '''","''' + name + '''","'''+ str(rows["id"]) +'''")''')
        jgrup = dict(newgrup)
    
        jmodul['newgrup'] = jgrup        
        
        conn.commit()
        jmodul['api_status'] = 1
    except sqlite3.OperationalError:
        jmodul['api_status'] = 0            
    
    conn.close()

    return jmodul

def rem_grup(slug):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''SELECT * FROM grups WHERE slug = "''' + slug + '''"''').fetchone()
    delid = str(rows["id"])
    rgrup = {}
    try:
        sql = '''DELETE FROM grups WHERE slug = "''' + slug + '''"'''
        rows = db.execute(sql)
        sql = '''DELETE FROM sensors WHERE grups_id = "''' + delid + '''"'''
        rows = db.execute(sql)
        
        conn.commit()        
        
        rgrup = dict(rows)
        rgrup['api_status'] = 1
    except sqlite3.OperationalError:
        rgrup['api_status'] = 0
    
    
    conn.close()

    return rgrup

def new_sensor( slug, name, pin, pin2, tipe_sensor_id):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rows = db.execute('''SELECT * FROM grups WHERE slug = "''' + slug + '''"''').fetchone()
    try:
        jgrup = dict(rows)
        sql = '''INSERT INTO sensors(slug,name,pin,pin2,tipe_sensor_id,grups_id) VALUES ("'''+ slugify(slug + "_" + name ) +  '''",
            "''' + name + '''","'''+ pin +'''","'''+ pin2 +'''","'''+ tipe_sensor_id +'''","'''+ str(rows["id"]) +'''")'''
        #print(sql)
        newsensor = db.execute(sql)
        jsensor = dict(newsensor)
    
        jgrup['newsensor'] = jsensor        
        
        conn.commit()
        jgrup['api_status'] = 1
    except sqlite3.OperationalError:
        jgrup['api_status'] = 0            
    
    conn.close()

    return jgrup

def rem_sensor(slug):
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    rsensor = {}
    try:
        sql = '''DELETE FROM sensors WHERE slug = "''' + slug + '''"'''
        #print(sql)
        rows = db.execute(sql)
        conn.commit()
        
        rsensor = dict(rows)
        rsensor['api_status'] = 1
    except sqlite3.OperationalError:
        rsensor['api_status'] = 0
    
    
    conn.close()

    return rsensor

def empty_logic():
    conn = sqlite3.connect(app_path+'cgi-bin/inderasqlite3.db')
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    elogic = {}
    try:
        sql = '''DELETE FROM logic'''
        #print(sql)
        rows = db.execute(sql)
        conn.commit()
        
        elogic = dict(rows)
        elogic['api_status'] = 1
    except sqlite3.OperationalError:
        elogic['api_status'] = 0
    
    
    conn.close()

    return elogic

